FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src \
    CHROMA_PATH=/app/data/chroma \
    INDEX_MANIFEST_PATH=/app/data/processed/index_manifest.json \
    CHECKPOINTER=memory

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src
RUN pip install .

# 免费托管没有兼容 RediSearch 的 Redis，索引随镜像打包，运行期只读检索
COPY --chown=1000:1000 data ./data

EXPOSE 8000

CMD ["uvicorn", "wanchain_agent.config:build_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
