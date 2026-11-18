FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src \
    CHROMA_PATH=/app/data/chroma \
    INDEX_MANIFEST_PATH=/app/data/processed/index_manifest.json

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
COPY src ./src
RUN pip install .

# 索引随镜像打包，运行期只做检索；重建索引后需要重新构建镜像
COPY data ./data

EXPOSE 8000

CMD ["uvicorn", "wanchain_agent.config:build_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
