# Muse Collector Worker

离线采集Worker，用于监听和执行数据采集任务。

## 功能

- 监听 `crawl_task` 表中的待执行任务 (task_status=1)
- 使用任务锁机制防止并发执行同一任务
- 从配置的数据源采集歌曲和歌手信息
- 将采集数据保存到快照表 (snap) 和正式表 (info)
- 更新任务状态和统计信息

## 运行

```bash
# 启动Worker
python worker/worker.py
```

Worker会持续运行，每隔 `worker_poll_interval` 秒（默认10秒）轮询一次待执行任务。

## 优雅关闭

Worker支持优雅关闭，可以通过以下方式停止：

- `Ctrl+C` (SIGINT)
- `kill <pid>` (SIGTERM)

## 配置

在 `.env` 文件中配置以下参数：

```env
# Worker配置
WORKER_POLL_INTERVAL=10      # 轮询间隔（秒）
WORKER_BATCH_SIZE=100        # 批处理大小
WORKER_MAX_RETRY=3           # 最大重试次数
WORKER_TIMEOUT=7200          # 任务超时时间（秒）
```

## 架构

### 组件

1. **TaskListener** - 任务监听器
   - 轮询待执行任务
   - 获取任务锁
   - 委托给CrawlerWorker处理

2. **TaskLock** - 任务锁
   - 基于数据库的分布式锁
   - 防止同一任务并发执行

3. **CrawlerWorker** - 爬虫Worker
   - 处理歌曲和歌手采集任务
   - 调用数据源适配器获取数据
   - 保存数据到snap表和info表

4. **AdapterRegistry** - 适配器注册表
   - 管理数据源适配器
   - 提供统一的适配器访问接口

### 数据流

```
TaskListener 
  → 查询待执行任务 (task_status=1)
  → 获取任务锁 (更新为task_status=2)
  → CrawlerWorker.process_task()
    → 读取target_ids
    → 遍历srcs数据源
    → 调用Adapter.fetch_song/fetch_artist()
    → 保存到snap表
    → 保存到info表
  → 更新任务状态 (task_status=3/4)
  → 释放任务锁
```

## 任务状态

- 1 = 等待执行
- 2 = 执行中
- 3 = 执行成功
- 4 = 执行失败
- 5 = 已取消

## 快照状态

- 0 = 初始
- 1 = 等待处理
- 2 = 处理中
- 3 = 成功
- 4 = 失败
- 5 = 已跳过

## 注意事项

1. **数据源适配器**: 需要先实现并注册数据源适配器（Task 3），Worker才能正常采集数据
2. **数据库连接**: 确保数据库连接配置正确
3. **并发控制**: 可以运行多个Worker实例，任务锁会自动防止冲突
4. **错误处理**: Worker会记录错误到日志和数据库，不会因单个任务失败而停止
