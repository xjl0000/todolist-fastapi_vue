# 数据库模型
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from database import Base

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)  # 待办内容不能为空
    completed = Column(Boolean, default=False)
    date = Column(String, index=True, nullable=False)  # YYYY-MM-DD 格式，按日期分组
    created_at = Column(DateTime, server_default=func.now())
