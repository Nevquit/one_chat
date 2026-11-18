# Wanchain Agent

FastAPI + LangGraph + Chroma 实现的 Wanchain 跨链与知识问答服务。

## Linux 部署（Docker Compose）

要求：Linux（x86_64 / arm64）、Docker 24+、Docker Compose v2，服务器可访问 PyPI、DeepSeek 与 SiliconFlow。

### 1. 上传代码

本地 PowerShell：

```powershell
tar -czf deploy.tar.gz --exclude=.venv --exclude=.git --exclude=corpus --exclude=tests Dockerfile docker-compose.yml .dockerignore pyproject.toml src data deploy
scp deploy.tar.gz user@server:~/
ssh user@server "mkdir -p ~/one_chat && tar -xzf ~/deploy.tar.gz -C ~/one_chat"
```

归档里包含约 11 MB 的 Chroma 索引，服务器不需要重新调用 embedding 建库。

### 2. 配置密钥

```bash
cd ~/one_chat
cp deploy/.env.example .env
chmod 600 .env
vi .env
```

至少填写 `LLM_API_KEY` 与 `EMBEDDING_API_KEY`。

### 3. 启动

```bash
docker compose up -d --build
docker compose ps
docker compose exec app python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8000/health').read().decode())"
```

Compose 把应用端口绑定到 `127.0.0.1:8000`，不会直接暴露公网。

### 4. 访问方式

临时验证用 SSH 隧道：

```powershell
ssh -L 8000:127.0.0.1:8000 user@server
```

然后本机访问 `http://127.0.0.1:8000/health`。

正式使用建议用 Nginx 或 Caddy 反向代理到 `127.0.0.1:8000`，并配置 HTTPS。

### 5. 更新

重新上传代码后：

```bash
docker compose up -d --build
```

## 运行结构

- `app`：FastAPI + LangGraph，读取镜像内的 Chroma 索引。
- `redis`：Redis 8，内置 RediSearch，保存会话检查点；数据写入 `redis-data` 卷。
- 两个服务都配置了健康检查，Redis 就绪后才启动应用。
- 默认单实例；Redis 卷用于跨容器重启恢复会话。

## 注意

- `.env` 含密钥，已加入 `.gitignore` 和 `.dockerignore`。
- 语料或切分参数变化后，需要本地重建 `data/` 并重新构建镜像。
- Docker 命令需要当前用户在 `docker` 组，或使用 `sudo`。
