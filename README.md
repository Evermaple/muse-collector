# Muse Collector

音乐数据采集系统，用于从各种数据源采集歌曲和歌手信息。

## 系统架构

- **在线服务**: FastAPI 提供 REST API 接口，用于任务管理和数据查询
- **离线服务**: Python Worker 脚本，监听任务并执行数据采集

## 项目结构

```
muse_collector/
├── api/                # API服务模块
├── worker/             # 离线采集Worker
├── models/             # 数据模型
├── utils/              # 工具模块
├── config/             # 配置管理
├── logs/               # 日志文件
├── requirements.txt    # Python依赖
├── .env.example        # 环境变量示例
└── README.md          # 项目文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息
vim .env
```

### 3. 初始化数据库

```bash
python scripts/init_db.py
```

### 4. 启动服务

**启动离线Worker:**
```bash
python worker.py
```

**启动API服务:**
```bash
python main.py
```

**访问API文档:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 技术栈

- **Python 3.8+**
- **FastAPI**: Web框架
- **pymysql**: MySQL数据库驱动
- **requests**: HTTP客户端
- **pydantic**: 数据验证
- **loguru**: 日志管理

## 数据源支持

- ✅ 网易云音乐 (Netease)
- 🔜 QQ音乐 (待扩展)
- 🔜 酷狗音乐 (待扩展)

## API接口

### 任务管理
- `POST /api/tasks` - 创建采集任务
- `GET /api/tasks` - 查询任务列表
- `GET /api/tasks/{task_id}` - 查询任务详情
- `PUT /api/tasks/{task_id}/cancel` - 取消任务
- `POST /api/tasks/{task_id}/retry` - 重试失败任务

### 数据查询
- `GET /api/songs` - 查询歌曲列表
- `GET /api/songs/{song_id}` - 查询歌曲详情
- `GET /api/artists` - 查询歌手列表
- `GET /api/artists/{artist_id}` - 查询歌手详情

## 核心功能

✅ **已实现功能**:
- 数据库连接池管理
- 数据模型和验证
- 网易云音乐适配器
- 离线采集Worker
- 数据验证和质量检查
- 错误处理和重试机制
- 任务监控和日志
- RESTful API服务
- 数据库初始化脚本
- 完整的部署文档

## 开发指南

详细的开发文档请参考：
- 需求文档: `.kiro/specs/muse-collector/requirements.md`
- 设计文档: `.kiro/specs/muse-collector/design.md`
- 任务列表: `.kiro/specs/muse-collector/tasks.md`
- 部署指南: `DEPLOYMENT.md`

## License

MIT
# MuseCollector
