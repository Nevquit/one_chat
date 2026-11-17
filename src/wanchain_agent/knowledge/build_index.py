r"""离线建库入口：扫描语料目录 → 清洗 → 切分 → 写 chunks.jsonl 与 manifest.json。

本轮只产出切分结果，不调用 embedding、不写向量库；下一轮在同一份 chunks 上
补 embedding 与索引写入即可，切分参数与语料指纹都已固化在 manifest 里。

用法：

```powershell
.\.venv\Scripts\python.exe -m wanchain_agent.knowledge.build_index --corpus corpus --out data/processed
```

契约：

- ``chunks.jsonl`` 每行一个 ``core.models.Chunk``，顺序稳定、``chunk_id`` 幂等；
- ``manifest.json`` 记录语料文件哈希、切分参数与构建时间，供启动时校验；
- 语料目录为空、文件非 UTF-8 等可预期问题一律抛 ``ValueError``，由 CLI 转为退出码。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from wanchain_agent.core.models import Chunk
from wanchain_agent.knowledge.chunker import (
    CHUNKER_VERSION,
    DEFAULT_MAX_TOKENS,
    DEFAULT_OVERLAP_TOKENS,
    TOKEN_ESTIMATOR,
    chunk_markdown,
)
from wanchain_agent.knowledge.cleaner import clean_markdown

MANIFEST_SCHEMA_VERSION = 1
CHUNKS_FILENAME = "chunks.jsonl"
MANIFEST_FILENAME = "manifest.json"
DEFAULT_CORPUS_DIR = "corpus"
DEFAULT_OUT_DIR = "data/processed"

_MARKDOWN_SUFFIXES = {".md", ".markdown"}


@dataclass(frozen=True)
class BuildResult:
    corpus_root: Path
    out_dir: Path
    file_count: int
    chunk_count: int
    manifest: dict[str, Any]

    @property
    def chunks_path(self) -> Path:
        return self.out_dir / CHUNKS_FILENAME

    @property
    def manifest_path(self) -> Path:
        return self.out_dir / MANIFEST_FILENAME


def build_index(
    corpus_dir: str | Path = DEFAULT_CORPUS_DIR,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    *,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    overlap_tokens: int = DEFAULT_OVERLAP_TOKENS,
    generated_at: str | None = None,
    git_commit: str | None = None,
) -> BuildResult:
    """构建切分产物。已存在的同名产物会被整体覆盖。"""
    root = Path(corpus_dir)
    if not root.is_dir():
        raise ValueError(f"语料目录不存在：{root}")

    files = _markdown_files(root)
    if not files:
        raise ValueError(f"语料目录中没有 Markdown 文件：{root}")

    chunks: list[Chunk] = []
    entries: list[dict[str, Any]] = []

    for path in files:
        relative = path.relative_to(root).as_posix()
        raw_bytes = path.read_bytes()
        try:
            raw = raw_bytes.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"文件不是 UTF-8 编码：{relative}") from exc

        file_chunks = chunk_markdown(
            clean_markdown(raw),
            doc_id=_doc_id(relative),
            source_path=relative,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )
        chunks.extend(file_chunks)
        entries.append(
            {
                "path": relative,
                "sha256": hashlib.sha256(raw_bytes).hexdigest(),
                "chunk_count": len(file_chunks),
            }
        )

    manifest: dict[str, Any] = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "generated_at": generated_at or datetime.now(UTC).isoformat(),
        "corpus": {
            "root": str(root.resolve()),
            "sha256": _corpus_hash(entries),
            "git_commit": git_commit,
            "file_count": len(entries),
            "files": entries,
        },
        "chunker": {
            "version": CHUNKER_VERSION,
            "token_estimator": TOKEN_ESTIMATOR,
            "max_tokens": max_tokens,
            "overlap_tokens": overlap_tokens,
        },
        "chunk_count": len(chunks),
    }

    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    _write_chunks(output / CHUNKS_FILENAME, chunks)
    (output / MANIFEST_FILENAME).write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return BuildResult(
        corpus_root=root,
        out_dir=output,
        file_count=len(entries),
        chunk_count=len(chunks),
        manifest=manifest,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="构建 RAG 离线切分产物（chunks.jsonl + manifest.json）")
    parser.add_argument("--corpus", default=DEFAULT_CORPUS_DIR, help="Markdown 语料目录")
    parser.add_argument("--out", default=DEFAULT_OUT_DIR, help="产物输出目录")
    parser.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_TOKENS)
    parser.add_argument("--overlap-tokens", type=int, default=DEFAULT_OVERLAP_TOKENS)
    args = parser.parse_args(argv)

    corpus = Path(args.corpus)
    try:
        result = build_index(
            corpus,
            args.out,
            max_tokens=args.max_tokens,
            overlap_tokens=args.overlap_tokens,
            git_commit=_git_commit(corpus),
        )
    except ValueError as exc:
        print(f"构建失败：{exc}", file=sys.stderr)
        return 1

    print(f"完成：{result.file_count} 个文件，{result.chunk_count} 个片段")
    print(f"产物：{result.chunks_path} / {result.manifest_path}")
    return 0


def _markdown_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in _MARKDOWN_SUFFIXES
        and not any(part.startswith(".") for part in path.relative_to(root).parts)
    )


def _doc_id(relative_path: str) -> str:
    """去掉扩展名的相对路径作为文档标识，跨构建稳定且可读。"""
    return relative_path.rsplit(".", 1)[0]


def _corpus_hash(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        digest.update(f"{entry['path']}\0{entry['sha256']}\n".encode())
    return digest.hexdigest()


def _write_chunks(path: Path, chunks: list[Chunk]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(chunk.model_dump_json() + "\n")


def _git_commit(path: Path) -> str | None:
    """尽力读取语料所在仓库的 commit；语料不是 git 仓库时返回 None。"""
    if not path.is_dir():
        return None
    try:
        completed = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip() or None


if __name__ == "__main__":
    raise SystemExit(main())
