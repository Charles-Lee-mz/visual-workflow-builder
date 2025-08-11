#!/usr/bin/env python3
"""
数据库迁移管理器
支持MySQL和SQLite数据库的自动迁移
"""

import os
import sqlite3
import logging
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False
    pymysql = None

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MigrationManager:
    """数据库迁移管理器"""
    
    def __init__(self, database_url: str, migrations_dir: str = "migrations"):
        """
        初始化迁移管理器
        
        Args:
            database_url: 数据库连接URL
            migrations_dir: 迁移脚本目录
        """
        self.database_url = database_url
        self.migrations_dir = Path(migrations_dir)
        self.engine = create_engine(database_url)
        self.is_sqlite = database_url.startswith('sqlite')
        self.is_mysql = database_url.startswith('mysql')
        
        # 确保迁移目录存在
        self.migrations_dir.mkdir(exist_ok=True)
        
    def get_applied_migrations(self) -> List[str]:
        """
        获取已应用的迁移版本列表
        
        Returns:
            已应用的迁移版本列表
        """
        try:
            with self.engine.connect() as conn:
                # 检查迁移表是否存在
                if self.is_sqlite:
                    result = conn.execute(text(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'"
                    ))
                else:
                    result = conn.execute(text(
                        "SELECT TABLE_NAME FROM information_schema.TABLES "
                        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'schema_migrations'"
                    ))
                
                if not result.fetchone():
                    return []
                
                # 获取已应用的迁移
                result = conn.execute(text("SELECT version FROM schema_migrations ORDER BY version"))
                return [row[0] for row in result.fetchall()]
                
        except SQLAlchemyError as e:
            logger.error(f"获取已应用迁移失败: {e}")
            return []
    
    def get_available_migrations(self) -> List[Dict[str, str]]:
        """
        获取可用的迁移文件列表
        
        Returns:
            迁移文件信息列表，包含版本号和文件路径
        """
        migrations = []
        
        # 根据数据库类型选择对应的迁移文件
        if self.is_sqlite:
            pattern = "*_sqlite.sql"
        else:
            pattern = "*.sql"
            
        for file_path in self.migrations_dir.glob(pattern):
            if self.is_sqlite and not file_path.name.endswith('_sqlite.sql'):
                continue
            if not self.is_sqlite and file_path.name.endswith('_sqlite.sql'):
                continue
                
            # 提取版本号（假设文件名格式为：001_description.sql）
            version = file_path.stem.split('_')[0]
            if self.is_sqlite and file_path.name.endswith('_sqlite.sql'):
                version = file_path.stem.replace('_sqlite', '').split('_')[0]
                
            migrations.append({
                'version': version,
                'file_path': str(file_path),
                'description': self._extract_description(file_path)
            })
        
        # 按版本号排序
        migrations.sort(key=lambda x: x['version'])
        return migrations
    
    def _extract_description(self, file_path: Path) -> str:
        """
        从迁移文件中提取描述信息
        
        Args:
            file_path: 迁移文件路径
            
        Returns:
            迁移描述
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip().startswith('-- 描述:'):
                        return line.strip().replace('-- 描述:', '').strip()
                    elif line.strip().startswith('-- Description:'):
                        return line.strip().replace('-- Description:', '').strip()
            return file_path.stem
        except Exception:
            return file_path.stem
    
    def apply_migration(self, migration_info: Dict[str, str]) -> bool:
        """
        应用单个迁移
        
        Args:
            migration_info: 迁移信息字典
            
        Returns:
            是否成功应用
        """
        version = migration_info['version']
        file_path = migration_info['file_path']
        description = migration_info['description']
        
        logger.info(f"应用迁移 {version}: {description}")
        
        try:
            # 读取迁移文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # 执行迁移
            with self.engine.begin() as conn:
                # 分割SQL语句（处理多个语句）
                statements = self._split_sql_statements(sql_content)
                
                for statement in statements:
                    if statement.strip():
                        conn.execute(text(statement))
                
                # 记录迁移版本（如果不是在迁移脚本中已经处理）
                if 'schema_migrations' not in sql_content.lower():
                    conn.execute(text(
                        "INSERT INTO schema_migrations (version, description) VALUES (:version, :description)"
                    ), {'version': version, 'description': description})
            
            logger.info(f"迁移 {version} 应用成功")
            return True
            
        except Exception as e:
            logger.error(f"应用迁移 {version} 失败: {e}")
            return False
    
    def _split_sql_statements(self, sql_content: str) -> List[str]:
        """
        分割SQL语句
        
        Args:
            sql_content: SQL文件内容
            
        Returns:
            SQL语句列表
        """
        # 简单的SQL语句分割（可能需要更复杂的解析）
        statements = []
        current_statement = []
        in_transaction = False
        
        for line in sql_content.split('\n'):
            line = line.strip()
            
            # 跳过注释和空行
            if not line or line.startswith('--'):
                continue
            
            current_statement.append(line)
            
            # 检查是否是语句结束
            if line.endswith(';') and not in_transaction:
                statements.append(' '.join(current_statement))
                current_statement = []
            elif 'BEGIN' in line.upper():
                in_transaction = True
            elif 'COMMIT' in line.upper() or 'ROLLBACK' in line.upper():
                in_transaction = False
                statements.append(' '.join(current_statement))
                current_statement = []
        
        # 添加最后一个语句（如果有）
        if current_statement:
            statements.append(' '.join(current_statement))
        
        return statements
    
    def migrate(self, target_version: Optional[str] = None) -> bool:
        """
        执行数据库迁移
        
        Args:
            target_version: 目标版本，如果为None则迁移到最新版本
            
        Returns:
            是否成功迁移
        """
        try:
            # 获取已应用和可用的迁移
            applied_migrations = set(self.get_applied_migrations())
            available_migrations = self.get_available_migrations()
            
            # 过滤需要应用的迁移
            pending_migrations = [
                migration for migration in available_migrations
                if migration['version'] not in applied_migrations
            ]
            
            if target_version:
                pending_migrations = [
                    migration for migration in pending_migrations
                    if migration['version'] <= target_version
                ]
            
            if not pending_migrations:
                logger.info("没有需要应用的迁移")
                return True
            
            # 应用迁移
            for migration in pending_migrations:
                if not self.apply_migration(migration):
                    return False
            
            logger.info(f"成功应用 {len(pending_migrations)} 个迁移")
            return True
            
        except Exception as e:
            logger.error(f"迁移失败: {e}")
            return False
    
    def rollback(self, target_version: str) -> bool:
        """
        回滚到指定版本
        
        Args:
            target_version: 目标版本
            
        Returns:
            是否成功回滚
        """
        # 简单实现，实际项目中需要更复杂的回滚逻辑
        logger.warning("回滚功能尚未完全实现")
        return False
    
    def status(self) -> Dict[str, any]:
        """
        获取迁移状态
        
        Returns:
            迁移状态信息
        """
        applied_migrations = self.get_applied_migrations()
        available_migrations = self.get_available_migrations()
        
        pending_migrations = [
            migration['version'] for migration in available_migrations
            if migration['version'] not in applied_migrations
        ]
        
        return {
            'database_type': 'SQLite' if self.is_sqlite else 'MySQL',
            'applied_count': len(applied_migrations),
            'pending_count': len(pending_migrations),
            'latest_applied': applied_migrations[-1] if applied_migrations else None,
            'pending_migrations': pending_migrations
        }

def create_migration_manager(database_url: str = None) -> MigrationManager:
    """
    创建迁移管理器的便捷函数
    
    Args:
        database_url: 数据库连接URL，如果为None则从环境变量获取
        
    Returns:
        迁移管理器实例
    """
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///workflow.db')
    
    return MigrationManager(database_url)

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库迁移管理器')
    parser.add_argument('command', choices=['migrate', 'status', 'rollback'], help='执行的命令')
    parser.add_argument('--target', help='目标版本')
    parser.add_argument('--database-url', help='数据库连接URL')
    
    args = parser.parse_args()
    
    # 创建迁移管理器
    manager = create_migration_manager(args.database_url)
    
    if args.command == 'migrate':
        success = manager.migrate(args.target)
        exit(0 if success else 1)
    elif args.command == 'status':
        status = manager.status()
        print(f"数据库类型: {status['database_type']}")
        print(f"已应用迁移: {status['applied_count']}")
        print(f"待应用迁移: {status['pending_count']}")
        if status['latest_applied']:
            print(f"最新版本: {status['latest_applied']}")
        if status['pending_migrations']:
            print(f"待应用版本: {', '.join(status['pending_migrations'])}")
    elif args.command == 'rollback':
        if not args.target:
            print("回滚命令需要指定目标版本")
            exit(1)
        success = manager.rollback(args.target)
        exit(0 if success else 1)