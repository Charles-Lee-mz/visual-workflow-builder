#!/usr/bin/env python3
"""
数据库初始化脚本
用于项目启动时自动初始化数据库和基础数据
"""

import os
import json
import logging
from typing import Dict, List, Any
from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from app.database.migration_manager import create_migration_manager
from app.models import (
    User, UserRole, UserStatus,
    NodeType,
    SystemConfig, ConfigType,
    WorkflowTemplate
)
from app.core.security import get_password_hash

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseInitializer:
    """数据库初始化器"""
    
    def __init__(self, database_url: str):
        """
        初始化数据库初始化器
        
        Args:
            database_url: 数据库连接URL
        """
        self.database_url = database_url
        self.engine = create_engine(database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.migration_manager = create_migration_manager(database_url)
        
    def init_database(self) -> bool:
        """
        初始化数据库
        
        Returns:
            是否成功初始化
        """
        try:
            logger.info("开始初始化数据库...")
            
            # 1. 执行数据库迁移
            logger.info("执行数据库迁移...")
            if not self.migration_manager.migrate():
                logger.error("数据库迁移失败")
                return False
            
            # 2. 初始化基础数据
            logger.info("初始化基础数据...")
            if not self._init_base_data():
                logger.error("基础数据初始化失败")
                return False
            
            logger.info("数据库初始化完成")
            return True
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return False
    
    def _init_base_data(self) -> bool:
        """
        初始化基础数据
        
        Returns:
            是否成功初始化
        """
        try:
            with self.SessionLocal() as session:
                # 初始化管理员用户
                self._init_admin_user(session)
                
                # 初始化节点类型
                self._init_node_types(session)
                
                # 初始化系统配置
                self._init_system_configs(session)
                
                # 初始化工作流模板
                self._init_workflow_templates(session)
                
                session.commit()
                
            return True
            
        except Exception as e:
            logger.error(f"基础数据初始化失败: {e}")
            return False
    
    def _init_admin_user(self, session) -> None:
        """
        初始化管理员用户
        
        Args:
            session: 数据库会话
        """
        # 检查是否已存在管理员用户
        admin_user = session.query(User).filter_by(role=UserRole.ADMIN).first()
        if admin_user:
            logger.info("管理员用户已存在，跳过创建")
            return
        
        # 创建默认管理员用户
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin123456')
        admin_user = User(
            username='admin',
            email='admin@workflow.com',
            password_hash=get_password_hash(admin_password),
            display_name='系统管理员',
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        
        session.add(admin_user)
        logger.info(f"创建管理员用户: {admin_user.username}")
    
    def _init_node_types(self, session) -> None:
        """
        初始化节点类型
        
        Args:
            session: 数据库会话
        """
        # 检查是否已存在节点类型
        if session.query(NodeType).count() > 0:
            logger.info("节点类型已存在，跳过创建")
            return
        
        # 基础节点类型定义
        node_types_data = [
            {
                'type_name': 'start',
                'display_name': '开始节点',
                'category': 'control',
                'description': '工作流开始节点',
                'icon_url': '/icons/start.svg',
                'color': '#4CAF50',
                'default_config': {
                    'trigger_type': 'manual',
                    'auto_start': False
                },
                'input_schema': {},
                'output_schema': {
                    'type': 'object',
                    'properties': {
                        'timestamp': {'type': 'string'},
                        'trigger_data': {'type': 'object'}
                    }
                },
                'form_schema': {
                    'type': 'object',
                    'properties': {
                        'trigger_type': {
                            'type': 'string',
                            'enum': ['manual', 'schedule', 'webhook'],
                            'title': '触发类型'
                        }
                    }
                }
            },
            {
                'type_name': 'end',
                'display_name': '结束节点',
                'category': 'control',
                'description': '工作流结束节点',
                'icon_url': '/icons/end.svg',
                'color': '#F44336',
                'default_config': {
                    'success_message': '工作流执行完成'
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'result': {'type': 'object'}
                    }
                },
                'output_schema': {},
                'form_schema': {
                    'type': 'object',
                    'properties': {
                        'success_message': {
                            'type': 'string',
                            'title': '成功消息'
                        }
                    }
                }
            },
            {
                'type_name': 'http_request',
                'display_name': 'HTTP请求',
                'category': 'network',
                'description': '发送HTTP请求',
                'icon_url': '/icons/http.svg',
                'color': '#2196F3',
                'default_config': {
                    'method': 'GET',
                    'timeout': 30,
                    'retry_count': 3
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'url': {'type': 'string'},
                        'headers': {'type': 'object'},
                        'data': {'type': 'object'}
                    },
                    'required': ['url']
                },
                'output_schema': {
                    'type': 'object',
                    'properties': {
                        'status_code': {'type': 'integer'},
                        'response_data': {'type': 'object'},
                        'headers': {'type': 'object'}
                    }
                },
                'form_schema': {
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            'title': '请求URL',
                            'format': 'uri'
                        },
                        'method': {
                            'type': 'string',
                            'enum': ['GET', 'POST', 'PUT', 'DELETE'],
                            'title': '请求方法'
                        },
                        'timeout': {
                            'type': 'integer',
                            'title': '超时时间(秒)',
                            'minimum': 1,
                            'maximum': 300
                        }
                    }
                }
            },
            {
                'type_name': 'data_transform',
                'display_name': '数据转换',
                'category': 'data',
                'description': '转换和处理数据',
                'icon_url': '/icons/transform.svg',
                'color': '#FF9800',
                'default_config': {
                    'transform_type': 'json',
                    'script': ''
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'data': {'type': 'object'}
                    }
                },
                'output_schema': {
                    'type': 'object',
                    'properties': {
                        'transformed_data': {'type': 'object'}
                    }
                },
                'form_schema': {
                    'type': 'object',
                    'properties': {
                        'transform_type': {
                            'type': 'string',
                            'enum': ['json', 'javascript', 'python'],
                            'title': '转换类型'
                        },
                        'script': {
                            'type': 'string',
                            'title': '转换脚本',
                            'format': 'textarea'
                        }
                    }
                }
            },
            {
                'type_name': 'condition',
                'display_name': '条件判断',
                'category': 'logic',
                'description': '根据条件进行分支判断',
                'icon_url': '/icons/condition.svg',
                'color': '#9C27B0',
                'default_config': {
                    'condition_type': 'expression',
                    'expression': ''
                },
                'input_schema': {
                    'type': 'object',
                    'properties': {
                        'data': {'type': 'object'}
                    }
                },
                'output_schema': {
                    'type': 'object',
                    'properties': {
                        'result': {'type': 'boolean'},
                        'branch': {'type': 'string'}
                    }
                },
                'form_schema': {
                    'type': 'object',
                    'properties': {
                        'condition_type': {
                            'type': 'string',
                            'enum': ['expression', 'script'],
                            'title': '条件类型'
                        },
                        'expression': {
                            'type': 'string',
                            'title': '条件表达式'
                        }
                    }
                }
            }
        ]
        
        for node_data in node_types_data:
            node_type = NodeType(
                type_name=node_data['type_name'],
                display_name=node_data['display_name'],
                category=node_data['category'],
                description=node_data['description'],
                icon_url=node_data['icon_url'],
                color=node_data['color'],
                default_config=node_data['default_config'],
                input_schema=node_data['input_schema'],
                output_schema=node_data['output_schema'],
                form_schema=node_data['form_schema'],
                is_system=True,
                is_active=True
            )
            session.add(node_type)
        
        logger.info(f"创建 {len(node_types_data)} 个基础节点类型")
    
    def _init_system_configs(self, session) -> None:
        """
        初始化系统配置
        
        Args:
            session: 数据库会话
        """
        # 检查是否已存在系统配置
        if session.query(SystemConfig).count() > 0:
            logger.info("系统配置已存在，跳过创建")
            return
        
        # 系统配置定义
        configs_data = [
            {
                'config_key': 'system.name',
                'config_value': '工作流编辑器平台',
                'config_type': ConfigType.STRING,
                'description': '系统名称',
                'is_public': True
            },
            {
                'config_key': 'system.version',
                'config_value': '1.0.0',
                'config_type': ConfigType.STRING,
                'description': '系统版本',
                'is_public': True
            },
            {
                'config_key': 'workflow.max_execution_time',
                'config_value': '3600',
                'config_type': ConfigType.NUMBER,
                'description': '工作流最大执行时间(秒)',
                'is_public': False
            },
            {
                'config_key': 'workflow.max_concurrent_executions',
                'config_value': '10',
                'config_type': ConfigType.NUMBER,
                'description': '最大并发执行数',
                'is_public': False
            },
            {
                'config_key': 'file.max_upload_size',
                'config_value': '10485760',
                'config_type': ConfigType.NUMBER,
                'description': '文件最大上传大小(字节)',
                'is_public': False
            },
            {
                'config_key': 'security.session_timeout',
                'config_value': '86400',
                'config_type': ConfigType.NUMBER,
                'description': '会话超时时间(秒)',
                'is_public': False
            },
            {
                'config_key': 'features.enabled',
                'config_value': json.dumps({
                    'workflow_sharing': True,
                    'template_marketplace': True,
                    'real_time_monitoring': True,
                    'api_access': True
                }),
                'config_type': ConfigType.JSON,
                'description': '功能开关配置',
                'is_public': True
            }
        ]
        
        for config_data in configs_data:
            config = SystemConfig(
                config_key=config_data['config_key'],
                config_value=config_data['config_value'],
                config_type=config_data['config_type'],
                description=config_data['description'],
                is_public=config_data['is_public']
            )
            session.add(config)
        
        logger.info(f"创建 {len(configs_data)} 个系统配置")
    
    def _init_workflow_templates(self, session) -> None:
        """
        初始化工作流模板
        
        Args:
            session: 数据库会话
        """
        # 检查是否已存在工作流模板
        if session.query(WorkflowTemplate).count() > 0:
            logger.info("工作流模板已存在，跳过创建")
            return
        
        # 基础工作流模板
        templates_data = [
            {
                'name': '简单HTTP请求工作流',
                'description': '演示如何创建一个简单的HTTP请求工作流',
                'category': 'example',
                'tags': ['http', 'api', '示例'],
                'template_data': {
                    'nodes': [
                        {
                            'id': 'start_1',
                            'type': 'start',
                            'position': {'x': 100, 'y': 100},
                            'data': {'label': '开始'}
                        },
                        {
                            'id': 'http_1',
                            'type': 'http_request',
                            'position': {'x': 300, 'y': 100},
                            'data': {
                                'label': 'HTTP请求',
                                'config': {
                                    'url': 'https://api.github.com/users/octocat',
                                    'method': 'GET'
                                }
                            }
                        },
                        {
                            'id': 'end_1',
                            'type': 'end',
                            'position': {'x': 500, 'y': 100},
                            'data': {'label': '结束'}
                        }
                    ],
                    'edges': [
                        {
                            'id': 'e1-2',
                            'source': 'start_1',
                            'target': 'http_1'
                        },
                        {
                            'id': 'e2-3',
                            'source': 'http_1',
                            'target': 'end_1'
                        }
                    ]
                },
                'is_featured': True,
                'is_public': True
            },
            {
                'name': '数据处理工作流',
                'description': '演示数据转换和条件判断的工作流',
                'category': 'example',
                'tags': ['数据处理', '条件判断', '示例'],
                'template_data': {
                    'nodes': [
                        {
                            'id': 'start_1',
                            'type': 'start',
                            'position': {'x': 100, 'y': 100},
                            'data': {'label': '开始'}
                        },
                        {
                            'id': 'transform_1',
                            'type': 'data_transform',
                            'position': {'x': 300, 'y': 100},
                            'data': {
                                'label': '数据转换',
                                'config': {
                                    'transform_type': 'json',
                                    'script': 'return {"processed": true, "data": input.data}'
                                }
                            }
                        },
                        {
                            'id': 'condition_1',
                            'type': 'condition',
                            'position': {'x': 500, 'y': 100},
                            'data': {
                                'label': '条件判断',
                                'config': {
                                    'condition_type': 'expression',
                                    'expression': 'data.processed === true'
                                }
                            }
                        },
                        {
                            'id': 'end_1',
                            'type': 'end',
                            'position': {'x': 700, 'y': 100},
                            'data': {'label': '结束'}
                        }
                    ],
                    'edges': [
                        {
                            'id': 'e1-2',
                            'source': 'start_1',
                            'target': 'transform_1'
                        },
                        {
                            'id': 'e2-3',
                            'source': 'transform_1',
                            'target': 'condition_1'
                        },
                        {
                            'id': 'e3-4',
                            'source': 'condition_1',
                            'target': 'end_1'
                        }
                    ]
                },
                'is_featured': True,
                'is_public': True
            }
        ]
        
        for template_data in templates_data:
            template = WorkflowTemplate(
                name=template_data['name'],
                description=template_data['description'],
                category=template_data['category'],
                tags=template_data['tags'],
                template_data=template_data['template_data'],
                is_featured=template_data['is_featured'],
                is_public=template_data['is_public']
            )
            session.add(template)
        
        logger.info(f"创建 {len(templates_data)} 个工作流模板")

def init_database(database_url: str = None) -> bool:
    """
    初始化数据库的便捷函数
    
    Args:
        database_url: 数据库连接URL，如果为None则从环境变量获取
        
    Returns:
        是否成功初始化
    """
    if database_url is None:
        database_url = os.getenv('DATABASE_URL', 'sqlite:///workflow.db')
    
    initializer = DatabaseInitializer(database_url)
    return initializer.init_database()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='数据库初始化脚本')
    parser.add_argument('--database-url', help='数据库连接URL')
    parser.add_argument('--force', action='store_true', help='强制重新初始化')
    
    args = parser.parse_args()
    
    success = init_database(args.database_url)
    if success:
        print("数据库初始化成功")
        exit(0)
    else:
        print("数据库初始化失败")
        exit(1)