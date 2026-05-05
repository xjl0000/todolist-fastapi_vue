from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator
from typing import List
import datetime

# 导入我们自己写的数据库和模型
from database import engine, SessionLocal
from model import Base, Todo

# 创建数据库表（如果不存在的话）
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用实例
app = FastAPI(title="Todo List API", version="1.0")

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

class TodoUpdate(BaseModel):
    title: str
    completed: bool

class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: datetime.datetime
    
    @validator('created_at', pre=True)
    def format_created_at(cls, v):
        if isinstance(v, str):
            return v
        return v.isoformat() if hasattr(v, 'isoformat') else str(v)

    class Config:
        orm_mode = True  # 允许直接从 ORM 模型转换为 Pydantic 模型

# ------------------------------
# 4 个核心 CRUD 接口
# ------------------------------

# 1. 获取所有待办事项（按创建时间倒序）
@app.get("/api/todos", response_model=List[TodoResponse])
def read_todos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    todos = db.query(Todo).order_by(Todo.created_at.desc()).offset(skip).limit(limit).all()
    return todos

# 2. 新增待办事项
@app.post("/api/todos", response_model=TodoResponse)
def create_todo(todo: TodoCreate, db: Session = Depends(get_db)):
    db_todo = Todo(title=todo.title, completed=todo.completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# 3. 修改待办事项
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

# 4. 删除待办事项
@app.delete("/api/todos/{todo_id}")
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_todo = db.query(Todo).filter(Todo.id == todo_id).first()
    if db_todo is None:
        raise HTTPException(status_code=404, detail="待办事项不存在")
    
    db.delete(db_todo)
    db.commit()
    return {"message": "删除成功"}