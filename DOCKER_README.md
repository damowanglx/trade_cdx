# Docker使用指南

## 快速开始

### 1. 构建镜像
```bash
docker build -t quant-trading .
```

### 2. 运行容器
```bash
# 交互式运行
docker run -it --rm -v $(pwd)/data:/app/data quant-trading

# 后台运行
docker run -d --name quant-trading -v $(pwd)/data:/app/data quant-trading
```

### 3. 使用Docker Compose
```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 常用命令

```bash
# 进入容器
docker exec -it quant-trading bash

# 运行回测
docker exec quant-trading python scripts/run_full_backtest.py

# 运行测试
docker exec quant-trading python -m pytest tests/ -v

# 查看数据
docker exec quant-trading ls -la data/all_stocks/
```

## 数据持久化

数据目录已挂载到宿主机：
- `./data` -> `/app/data`
- `./logs` -> `/app/logs`
- `./reports` -> `/app/reports`

## 环境变量

可在docker-compose.yml中配置：
- `PYTHONPATH`: Python路径
- `PYTHONUNBUFFERED`: 实时输出日志
