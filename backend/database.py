# 数据库配置
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLite 数据库文件地址，会在当前目录生成 test.db 文件
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

# 创建数据库引擎（SQLite 特殊配置：check_same_thread=False）
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# 创建数据库会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 ORM 基类，所有模型都继承自它
Base = declarative_base()