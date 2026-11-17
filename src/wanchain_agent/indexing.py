r"""RAG 离线建库组合根：chunks.jsonl → embedding → Chroma，并写索引清单。

这是离线链路的第二段，输入是 ``knowledge.build_index`` 产出的
``chunks.jsonl`` 与 ``manifest.json``，输出是向量库与 ``index_manifest.json``。

本模块属于组合根，允许直接装配适配器；切分、embedding、写入的细节分别
由 ``knowledge`` 与 ``adapters`` 负责，这里只做编排与一致性校验：

- 片段 id 不得重复，文本不得为空；
- 向量条数、维度必须与片段和配置一致；
- 写入后索引条数必须等于片段条数；
- 索引清单记录模型名、维度、语料哈希与切分参数，供启动时比对。

用法：

```powershell
.\.venv\Scripts\python.exe -m wanchain_agent.indexing --processed data/processed --chroma data/chroma
```
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wanchain_agent.adapters.index_chroma import ChromaVectorIndex
from wanchain_agent.config import Settings, build_embedding
from wanchain_agent.core.errors import AgentError
from wanchain_agent.core.models import Chunk
from wanchain_agent.core.ports import EmbeddingPort, VectorIndexPort
from wanchain_agent.knowledge.build_index import (
    CHUNKS_FILENAME,
    MANIFEST_FILENAME,
)

INDEX_MANIFEST_SCHEMA_VERSION = 1
INDEX_MANIFEST_FILENAME = "index_manifest.json"
DEFAULT_PROCESSED_DIR = "data/processed"


@dataclass(frozen=True)
class IndexBuildResult:
    processed_dir: Path
    chunk_count: int
    vector_dimension: int
    model_name: str
    manifest: dict[str, Any]

    @property
    def manifest_path(self) -> Path:
        return self.processed_dir / INDEX_MANIFEST_FILENAME


def load_chunks(path: str | Path) -> list[Chunk]:
    """读取 ``chunks.jsonl``，逐行校验。"""
    source = Path(path)
    if not source.is_file():
        raise ValueError(f"找不到切分产物：{source}")

    chunks: list[Chunk] = []
    for line_number, line in enumerate(
        source.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not line.strip():
            continue
        try:
            chunks.append(Chunk.model_validate_json(line))
        except ValueError as exc:
            raise ValueError(f"{source} 第 {line_number} 行不是合法片段") from exc

    _check_unique(chunks)
    return chunks


async def index_chunks(
    chunks: list[Chunk],
    *,
    embedding: EmbeddingPort,
    index: VectorIndexPort,
) -> int:
    """向量化并写入索引，返回写入条数。"""
    _check_unique(chunks)
    if not chunks:
        return 0

    vectors = await embedding.embed_documents([chunk.text for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError(
            f"向量条数与片段条数不一致：{len(vectors)} != {len(chunks)}"
        )
    for position, vector in enumerate(vectors):
        if len(vector) != embedding.dimension:
            raise ValueError(
                f"第 {position} 条向量维度不符：{len(vector)} != {embedding.dimension}"
            )

    written = index.write(chunks, vectors)
    if written != len(chunks):
        raise ValueError(f"写入条数与片段条数不一致：{written} != {len(chunks)}")
    if index.count() != len(chunks):
        raise ValueError(
            f"索引条数与片段条数不一致：{index.count()} != {len(chunks)}"
        )
    return written


async def build_vector_index(
    processed_dir: str | Path = DEFAULT_PROCESSED_DIR,
    *,
    embedding: EmbeddingPort,
    index: VectorIndexPort,
    generated_at: str | None = None,
) -> IndexBuildResult:
    """读取切分产物，构建向量索引并写出索引清单。"""
    directory = Path(processed_dir)
    source_manifest = _read_manifest(directory / MANIFEST_FILENAME)
    chunks_path = directory / CHUNKS_FILENAME
    chunks = load_chunks(chunks_path)

    written = await index_chunks(chunks, embedding=embedding, index=index)

    manifest: dict[str, Any] = {
        "schema_version": INDEX_MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "embedding": {
            "model_name": embedding.model_name,
            "dimension": embedding.dimension,
        },
        "chunks": {
            "count": written,
            "sha256": hashlib.sha256(chunks_path.read_bytes()).hexdigest(),
        },
        "corpus": source_manifest.get("corpus"),
        "chunker": source_manifest.get("chunker"),
    }
    (directory / INDEX_MANIFEST_FILENAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return IndexBuildResult(
        processed_dir=directory,
        chunk_count=written,
        vector_dimension=embedding.dimension,
        model_name=embedding.model_name,
        manifest=manifest,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="构建 RAG 向量索引（chunks.jsonl → Chroma + index_manifest.json）"
    )
    parser.add_argument("--processed", default=DEFAULT_PROCESSED_DIR, help="切分产物目录")
    parser.add_argument("--chroma", default=None, help="Chroma 持久化目录，默认读取 CHROMA_PATH")
    parser.add_argument("--collection", default=None, help="collection 名称，默认读取配置")
    args = parser.parse_args(argv)

    settings = Settings.from_env()
    try:
        result = asyncio.run(_run(args, settings))
    except (ValueError, AgentError) as exc:
        print(f"建库失败：{exc}", file=sys.stderr)
        return 1

    print(
        f"完成：{result.chunk_count} 个片段，"
        f"模型 {result.model_name}（{result.vector_dimension} 维）"
    )
    print(f"清单：{result.manifest_path}")
    return 0


async def _run(args: argparse.Namespace, settings: Settings) -> IndexBuildResult:
    embedding = build_embedding(settings)
    index = ChromaVectorIndex(
        persist_path=args.chroma or settings.chroma_path,
        collection_name=args.collection or settings.chroma_collection,
        metadata={
            "embedding_model": embedding.model_name,
            "embedding_dimension": embedding.dimension,
        },
    )
    try:
        return await build_vector_index(
            args.processed,
            embedding=embedding,
            index=index,
        )
    finally:
        index.close()
        closer = getattr(embedding, "aclose", None)
        if closer is not None:
            await closer()


def _read_manifest(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"找不到切分清单：{path}，请先运行 knowledge.build_index")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"切分清单不是合法 JSON：{path}") from exc
    if not isinstance(data, dict):
        # 文件内容错误，不是调用方类型错误，按数据错误处理。
        raise ValueError(f"切分清单结构不合法：{path}")  # noqa: TRY004
    return data


def _check_unique(chunks: list[Chunk]) -> None:
    seen: set[str] = set()
    for chunk in chunks:
        if chunk.chunk_id in seen:
            raise ValueError(f"片段 id 重复：{chunk.chunk_id}")
        seen.add(chunk.chunk_id)


if __name__ == "__main__":
    raise SystemExit(main())
