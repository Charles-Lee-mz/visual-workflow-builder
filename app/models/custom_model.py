from app.database import db
from datetime import datetime

class CustomModel(db.Model):
    """用户自定义模型表"""
    __tablename__ = 'custom_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='模型名称')
    provider = db.Column(db.String(50), nullable=False, comment='提供商')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    is_global = db.Column(db.Boolean, default=False, comment='是否为全局模型（所有用户可见）')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关联关系
    user = db.relationship('User', backref='custom_models')
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'name': self.name,
            'provider': self.provider,
            'user_id': self.user_id,
            'is_global': self.is_global,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user': {
                'id': self.user.id,
                'username': self.user.username
            } if self.user else None
        }
    
    def __repr__(self):
        return f'<CustomModel {self.name} ({self.provider})>'