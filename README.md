# 结构化工作流构建平台

一个基于React和Flask的现代化结构化工作流构建平台，支持可视化节点编辑、自然语言工作流生成和实时执行监控。

## 🎯 项目概述

本项目是一个全栈工作流管理系统，结合了前端可视化编辑器和后端智能处理引擎，为用户提供直观、高效的工作流设计和执行体验。

## 🚀 功能特性

### 核心功能
- **意图识别引擎**: 基于大模型的中文自然语言意图识别
- **可视化工作流设计**: 拖拽式工作流编辑器
- **自动化执行**: 支持多种节点类型的工作流执行
- **用户管理**: JWT认证和用户权限管理
- **模型配置**: 支持多种AI模型提供商

### 支持的节点类型
- 开始/结束节点
- 任务节点
- 条件判断节点
- 查询订单节点
- 转人工服务节点
- 加入群聊节点
- 获取兑换码节点
- 升级服务节点

### 支持的AI模型
- 通义千问 (Qwen)
- DeepSeek
- 豆包 (Doubao)
- OpenAI GPT

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Flask + SQLAlchemy
- **数据库**: MySQL / SQLite
- **缓存**: Redis
- **任务队列**: Celery
- **WebSocket**: Flask-SocketIO
- **API文档**: Swagger

### 前端技术栈
- **框架**: React 18 + TypeScript
- **状态管理**: Zustand
- **可视化**: React Flow
- **UI组件**: Ant Design
- **构建工具**: Vite
- **代码规范**: ESLint + Prettier

## 📦 安装部署

### 环境要求
- Python 3.8+
- Node.js 16+
- MySQL 8.0+ (生产环境) / SQLite (开发环境)
- Redis (可选)

### 后端安装
```bash
# 克隆项目
git clone https://github.com/Charles-Lee-mz/visual-workflow-builder.git
cd visual-workflow-builder

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和API密钥

# 初始化数据库
python create_db.py

# 启动后端服务
python run.py
```

### 前端安装
```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start
```

## 🔧 配置说明

### 环境变量配置
创建 `.env` 文件并配置以下变量：

```env
# 数据库配置
DATABASE_URL=mysql://username:password@localhost/workflow_db

# AI模型配置
QWEN_API_KEY=your-qwen-api-key
DEEPSEEK_API_KEY=your-deepseek-api-key
DOUBAO_API_KEY=your-doubao-api-key
OPENAI_API_KEY=your-openai-api-key

# 应用配置
SECRET_KEY=your-secret-key
FLASK_ENV=development
```

## 📖 使用指南

### 创建工作流
1. 访问 `http://localhost:3000`
2. 点击「新建工作流」
3. 拖拽节点到画布
4. 连接节点创建流程
5. 配置节点参数
6. 保存并测试工作流

### 自然语言创建
1. 点击「智能创建」
2. 输入自然语言描述
3. 系统自动生成工作流
4. 调整和优化流程

## 🧪 测试

```bash
# 后端测试
pytest

# 前端测试
cd frontend
npm test
```

## 📝 API 文档

启动后端服务后，访问 `http://localhost:5001/docs` 查看完整的API文档。

## 🤝 贡献指南

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [React Flow](https://reactflow.dev/) - 强大的流程图库
- [Ant Design](https://ant.design/) - 优秀的UI组件库
- [Flask](https://flask.palletsprojects.com/) - 轻量级Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL工具包

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件到项目维护者
- 加入讨论群组

---

⭐ 如果这个项目对你有帮助，请给它一个星标！