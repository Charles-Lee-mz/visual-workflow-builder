"""数据库实例"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# 创建数据库实例
db = SQLAlchemy()
migrate = Migrate()

def init_db(app):
    """初始化数据库"""
    db.init_app(app)
    migrate.init_app(app, db)
    return db