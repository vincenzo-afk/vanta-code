"""NetworkX knowledge graph: files, functions, classes, imports."""

from __future__ import annotations

import pickle
from pathlib import Path

import networkx as nx


class CodeGraph:
    """
    Directed graph representing relationships between code entities.

    Nodes: files, functions, classes
    Edges: defines (file → function), imports (file → module)
    """

    def __init__(self, graph_path: str):
        self.path = Path(graph_path)
        self.G: nx.DiGraph = self._load()

    def _load(self) -> nx.DiGraph:
        if self.path.exists():
            try:
                with open(self.path, "rb") as f:
                    return pickle.load(f)
            except Exception:
                pass
        return nx.DiGraph()

    def save(self) -> None:
        """Serialize the graph to disk."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "wb") as f:
            pickle.dump(self.G, f)

    def add_file(self, path: str, language: str) -> None:
        self.G.add_node(path, type="file", language=language)

    def add_function(self, name: str, file: str, start_line: int, end_line: int) -> None:
        node_id = f"{file}::{name}"
        self.G.add_node(node_id, type="function", file=file, start=start_line, end=end_line)
        self.G.add_edge(file, node_id, relation="defines")

    def add_class(self, name: str, file: str, start_line: int, end_line: int) -> None:
        node_id = f"{file}::class::{name}"
        self.G.add_node(node_id, type="class", file=file, start=start_line, end=end_line)
        self.G.add_edge(file, node_id, relation="defines")

    def add_import(self, from_file: str, imported_module: str) -> None:
        self.G.add_edge(from_file, imported_module, relation="imports")

    def get_related(self, file: str, depth: int = 2) -> list[str]:
        """Return all node IDs within `depth` hops from a file node."""
        if file not in self.G:
            return []
        ego = nx.ego_graph(self.G, file, radius=depth, undirected=True)
        return [n for n in ego.nodes() if n != file]

    def get_stats(self) -> dict:
        return {
            "nodes": self.G.number_of_nodes(),
            "edges": self.G.number_of_edges(),
        }
