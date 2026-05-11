# Muse Collector 部署指南

## 系统要求

### 软件依赖
- Python 3.8+
- MySQL 5.7+
- pip (Python包管理器)

### 硬件建议
- CPU: 2核+
- 内存: 4GB+
- 磁盘: 20GB+

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd muse_collector
```

### 2. 创建虚拟环境（推荐）

```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置数据库连接等信息
vim .env
```

必须配置的环境变量：
- `DB_HOST`: MySQL主机地址
- `DB_PORT`: MySQL端口（默认3306）
- `DB_USER`: 数据库用户名
- `DB_PASSWORD`: 数据库密码
- `DB_NAME`: 数据库名称（默认muse_collector）

### 5. 初始化数据库

```bash
# 方式1: 使用Python脚本（推荐）
python scripts/init_db.py

# 方式2: 直接执行SQL文件
mysql -h <host> -u <user> -p < scripts/init_db.sql
```

### 6. 验证安装

```bash
# 测试数据库连接
python -c "from utils.db_pool import db_pool; print('DB Health:', db_pool.check_health())"
```

## 启动服务

### 启动离线Worker

```bash
# 前台运行
python worker.py

# 后台运行（Linux/Mac）
nohup python worker.py > logs/worker.log 2>&1 &

# 查看日志
tail -f logs/worker.log
```

### 启动API服务（待实现）

```bash
# 前台运行
python main.py

# 后台运行
nohup python main.py > logs/api.log 2>&1 &
```

## 停止服务

### 优雅停止Worker

```bash
# 发送SIGTERM信号
kill -TERM <pid>

# 或使用pkill
pkill -f "python worker.py"
```

Worker会在收到信号后：
1. 停止接收新任务
2. 完成当前正在处理的任务
3. 关闭数据库连接
4. 退出进程

### 强制停止

```bash
kill -9 <pid>
```

## 配置说明

### Worker配置

在 `.env` 文件中配置：

```bash
# Worker轮询间隔（秒）
WORKER_POLL_INTERVAL=10

# 每次处理的批量大小
WORKER_BATCH_SIZE=100

# 最大重试次数
WORKER_MAX_RETRY=3

# 任务超时时间（秒）
WORKER_TIMEOUT=7200
```

### 日志配置

```bash
# 日志级别: DEBUG, INFO, WARNING, ERROR
LOG_LEVEL=INFO

# 日志目录
LOG_DIR=logs

# 日志轮转大小
LOG_ROTATION=500 MB

# 日志保留时间
LOG_RETENTION=30 days
```

### 数据源配置

```bash
# 网易云音乐
NETEASE_BASE_URL=https://music.163.com/api
NETEASE_RATE_LIMIT=100
NETEASE_TIMEOUT=30
```

## 监控和维护

### 查看日志

```bash
# 实时查看日志
tail -f logs/<date>.log

# 查看最近100行
tail -n 100 logs/<date>.log

# 搜索错误日志
grep "ERROR" logs/<date>.log
```

### 监控任务状态

```bash
# 查询待处理任务
mysql -h <host> -u <user> -p -D muse_collector -e "SELECT * FROM crawl_task WHERE task_status=1;"

# 查询执行中任务
mysql -h <host> -u <user> -p -D muse_collector -e "SELECT * FROM crawl_task WHERE task_status=2;"

# 查询失败任务
mysql -h <host> -u <user> -p -D muse_collector -e "SELECT * FROM crawl_task WHERE task_status=4;"
```

### 数据库维护

```bash
# 清理旧的快照数据（保留最近30天）
mysql -h <host> -u <user> -p -D muse_collector -e "DELETE FROM song_crawl_snap WHERE ctime < DATE_SUB(NOW(), INTERVAL 30 DAY);"
mysql -h <host> -u <user> -p -D muse_collector -e "DELETE FROM artist_crawl_snap WHERE ctime < DATE_SUB(NOW(), INTERVAL 30 DAY);"

# 优化表
mysql -h <host> -u <user> -p -D muse_collector -e "OPTIMIZE TABLE song_info, artist_info, crawl_task;"
```

## 常见问题

### 1. 数据库连接失败

**问题**: `Failed to initialize database pool`

**解决方案**:
- 检查 `.env` 中的数据库配置是否正确
- 确认MySQL服务是否运行
- 检查网络连接和防火墙设置
- 验证数据库用户权限

### 2. Worker无法启动

**问题**: Worker启动后立即退出

**解决方案**:
- 查看日志文件获取详细错误信息
- 确认数据库已正确初始化
- 检查Python依赖是否完整安装

### 3. 采集失败率高

**问题**: 大量任务失败

**解决方案**:
- 检查网络连接
- 查看数据源API是否可访问
- 检查是否触发了速率限制
- 调整 `WORKER_MAX_RETRY` 和超时配置

### 4. 内存占用过高

**问题**: Worker内存持续增长

**解决方案**:
- 减小 `WORKER_BATCH_SIZE`
- 定期重启Worker
- 检查是否有内存泄漏（查看日志）

### 5. 数据库连接池耗尽

**问题**: `Failed to get connection from pool`

**解决方案**:
- 增加 `DB_POOL_MAX_SIZE`
- 检查是否有连接未正确释放
- 减少并发Worker数量

## 性能优化

### 1. 数据库优化

```sql
-- 添加索引（如果查询慢）
CREATE INDEX idx_custom ON song_info(field_name);

-- 分析表
ANALYZE TABLE song_info, artist_info;
```

### 2. Worker优化

- 根据服务器性能调整 `WORKER_BATCH_SIZE`
- 多个Worker实例并行处理（确保任务锁机制正常）
- 使用SSD存储提升数据库性能

### 3. 网络优化

- 使用CDN或代理加速数据源访问
- 调整 `NETEASE_RATE_LIMIT` 避免触发限流
- 增加超时时间应对慢速网络

## 升级指南

### 1. 备份数据

```bash
# 备份数据库
mysqldump -h <host> -u <user> -p muse_collector > backup_$(date +%Y%m%d).sql
```

### 2. 停止服务

```bash
# 优雅停止所有Worker
pkill -TERM -f "python worker.py"
```

### 3. 更新代码

```bash
git pull origin main
```

### 4. 更新依赖

```bash
pip install -r requirements.txt --upgrade
```

### 5. 数据库迁移（如有）

```bash
# 执行迁移脚本
python scripts/migrate.py
```

### 6. 重启服务

```bash
python worker.py
```

## 安全建议

1. **不要将 `.env` 文件提交到版本控制**
2. **使用强密码**：数据库密码应足够复杂
3. **限制数据库访问**：只允许必要的IP访问
4. **定期备份**：建立自动备份机制
5. **监控日志**：定期检查异常日志
6. **更新依赖**：及时更新Python包修复安全漏洞

## 技术支持

如遇到问题，请：
1. 查看日志文件获取详细错误信息
2. 参考本文档的常见问题部分
3. 查看项目README和设计文档
4. 提交Issue到项目仓库

## 附录

### 目录结构

```
muse_collector/
├── api/                # API服务模块
├── worker/             # Worker模块
│   ├── adapters/       # 数据源适配器
│   ├── crawler.py      # 爬虫逻辑
│   ├── task_listener.py # 任务监听器
│   └── worker.py       # Worker主类
├── models/             # 数据模型
├── utils/              # 工具模块
├── config/             # 配置管理
├── scripts/            # 脚本
├── logs/               # 日志目录
├── worker.py           # Worker启动脚本
├── main.py             # API启动脚本
├── requirements.txt    # 依赖列表
├── .env                # 环境变量
└── README.md           # 项目说明
```

### 进程管理（使用systemd）

创建服务文件 `/etc/systemd/system/muse-worker.service`:

```ini
[Unit]
Description=Muse Collector Worker
After=network.target mysql.service

[Service]
Type=simple
User=<your-user>
WorkingDirectory=/path/to/muse_collector
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/python worker.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用和管理服务：

```bash
# 重载systemd配置
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start muse-worker

# 设置开机自启
sudo systemctl enable muse-worker

# 查看状态
sudo systemctl status muse-worker

# 查看日志
sudo journalctl -u muse-worker -f
```
