from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
import datetime

# 导入我们自己写的数据库和模型
from database import engine, SessionLocal
from model import Base, Todo

# 创建数据库表（如果不存在的话）
Base.metadata.create_all(bind=engine)

# 数据库迁移：如果旧表没有 date 列，自动添加
with engine.connect() as conn:
    result = conn.execute(text("PRAGMA table_info(todos)"))
    columns = [row[1] for row in result]
    if 'date' not in columns:
        today = datetime.date.today().isoformat()
        conn.execute(text(f"ALTER TABLE todos ADD COLUMN date TEXT DEFAULT '{today}'"))
        # 将已有记录的 date 设为今天
        conn.execute(text(f"UPDATE todos SET date = '{today}' WHERE date IS NULL"))
        conn.commit()

# 创建 FastAPI 应用实例
app = FastAPI(title="Todo List API", version="2.0")

# 配置 CORS 跨域（允许所有来源访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源访问（生产环境可限制具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 数据库依赖：获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic 数据模型：用于请求和响应的数据验证
class TodoCreate(BaseModel):
    title: str
    completed: bool = False
    date: Optional[str] = None  # YYYY-MM-DD，默认今天

class TodoUpdate(BaseModel):
    title: str
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    date: str
    created_at: datetime.datetime

    class Config:
        from_attributes = True

class DateStatus(BaseModel):
    date: str
    total: int
    completed: int
    all_completed: bool

# ------------------------------
# API 接口
# ------------------------------

# 1. 获取指定日期的待办事项（默认今天）
@app.get("/api/todos", response_model=List[TodoResponse])
def read_todos(date: Optional[str] = None, db: Session = Depends(get_db)):
    if date is None:
        date = datetime.date.today().isoformat()
    todos = db.query(Todo).filter(Todo.date == date).order_by(Todo.created_at.desc()).all()
    return todos

# 2. 获取所有有待办的日期及完成状态
@app.get("/api/dates", response_model=List[DateStatus])
def get_dates(db: Session = Depends(get_db)):
    dates = db.query(Todo.date).distinct().all()
    result = []
    for (date,) in dates:
        total = db.query(Todo).filter(Todo.date == date).count()
        completed = db.query(Todo).filter(Todo.date == date, Todo.completed == True).count()
        result.append(DateStatus(
            date=date,
            total=total,
            completed=completed,
            all_completed=(total > 0 and total == completed)
        ))
    result.sort(key=lambda x: x.date, reverse=True)
    return result

# 3. 新增待办事项
@app.post("/api/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    date = todo.date or datetime.date.today().isoformat()
    db_todo = Todo(title=todo.title, completed=todo.completed, date=date)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# 4. 修改待办事项
@app.put("/api/todos/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, todo: TodoUpdate, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    db_todo.title = todo.title
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo

# 5. 删除待办事项
@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "删除成功"}