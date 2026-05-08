"""Codebase indexer — walks project files, chunks, embeds, and stores."""

from __future__ import annotations

import hashlib
import fnmatch
from pathlib import Path

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

from vanta.memory.chroma_store import ChromaStore
from vanta.memory.embedder import embed
from vanta.memory.graph import CodeGraph
from vanta.utils.ast_utils import chunk_source, extract_python_symbols
from vanta.utils.logger import get_logger

console = Console()
log = get_logger("vanta.indexer")

LANGUAGE_MAP: dict[str, str] = {
    ".py": "python",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".rs": "rust",
    ".go": "go",
    ".md": "markdown",
    ".toml": "toml",
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
}


class Indexer:
    """
    Walks the project, chunks every relevant file, generates embeddings,
    stores them in ChromaDB, and builds the NetworkX knowledge graph.
    """

    def __init__(self, project_root: str, config=None):
        self.root = Path(project_root).resolve()
        self.config = config

        chroma_path = ".vanta/chroma"
        graph_path = ".vanta/graph.pkl"
        self.include_exts: list[str] = [".py", ".ts", ".js", ".md", ".toml", ".yaml"]
        self.exclude_patterns: list[str] = [
            "**/node_modules/**", "**/__pycache__/**", "**/.venv/**",
            "**/dist/**", "**/.git/**", "**/.vanta/**",
        ]
        self.chunk_size = 50  # lines per chunk
        self.chunk_overlap = 5

        if config and config.memory:
            chroma_path = config.memory.chroma_path
            graph_path = config.memory.graph_path
            self.include_exts = config.memory.include_extensions
            self.exclude_patterns = config.memory.exclude_patterns
            self.chunk_size = config.memory.chunk_size // 10 or 50
            self.chunk_overlap = config.memory.chunk_overlap // 10 or 5

        # Make paths absolute relative to project root
        if not Path(chroma_path).is_absolute():
            chroma_path = str(self.root / chroma_path)
        if not Path(graph_path).is_absolute():
            graph_path = str(self.root / graph_path)

        self.store = ChromaStore(chroma_path)
        self.graph = CodeGraph(graph_path)

    async def run(self) -> dict:
        """Run the full indexing pipeline. Returns stats dict."""
        files = self._collect_files()
        log.info(f"Found {len(files)} files to index")

        total_chunks = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.completed}/{task.total}"),
            console=console,
        ) as progress:
            task = progress.add_task("Indexing...", total=len(files))

            for file_path in files:
                try:
                    count = await self._index_file(file_path)
                    total_chunks += count
                except Exception as exc:
                    log.warning(f"Failed to index {file_path}: {exc}")
                finally:
                    progress.advance(task)

        self.graph.save()
        log.info(f"Indexed {len(files)} files, {total_chunks} chunks")
        stats = self.graph.get_stats()
        return {
            "files": len(files),
            "chunks": total_chunks,
            "graph_nodes": stats["nodes"],
            "graph_edges": stats["edges"],
        }

    def _collect_files(self) -> list[Path]:
        """Walk the project and collect all indexable files."""
        result: list[Path] = []
        for path in self.root.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in self.include_exts:
                continue
            rel = str(path.relative_to(self.root))
            if any(fnmatch.fnmatch(rel, pat.strip("**/")) or
                   fnmatch.fnmatch("/" + rel, pat) for pat in self.exclude_patterns):
                continue
            result.append(path)
        return result

    async def _index_file(self, file_path: Path) -> int:
        """Chunk, embed, and store a single file. Returns chunk count."""
        try:
            source = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return 0

        language = LANGUAGE_MAP.get(file_path.suffix, "text")
        rel_path = str(file_path.relative_to(self.root))

        # Update knowledge graph
        self.graph.add_file(rel_path, language)
        if language == "python":
            symbols = extract_python_symbols(source, str(file_path))
            for fn in symbols["functions"]:
                self.graph.add_function(fn["name"], rel_path, fn["start_line"], fn["end_line"])
            for cls in symbols["classes"]:
                self.graph.add_class(cls["name"], rel_path, cls["start_line"], cls["end_line"])
            for imp in symbols["imports"]:
                self.graph.add_import(rel_path, imp)

        # Chunk + embed + store
        chunks = chunk_source(source, chunk_size=self.chunk_size, overlap=self.chunk_overlap)
        if not chunks:
            return 0

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for start_line, end_line, content in chunks:
            chunk_id = hashlib.sha256(f"{rel_path}:{start_line}:{end_line}".encode()).hexdigest()[:32]
            ids.append(chunk_id)
            documents.append(content[:2000])  # Cap at 2k chars
            metadatas.append({
                "file": rel_path,
                "start_line": start_line,
                "end_line": end_line,
                "language": language,
            })

        embeddings = embed(documents)
        self.store.upsert(ids=ids, embeddings=embeddings, documents=documents, metadatas=metadatas)
        return len(chunks)
