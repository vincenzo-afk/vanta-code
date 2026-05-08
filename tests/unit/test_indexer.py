"""Unit tests for the memory indexer."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from vanta.memory.indexer import Indexer

def test_indexer_init():
    indexer = Indexer(project_root=".")
    assert indexer.project_root == Path(".").resolve()
    assert indexer.chunk_size == 1000

@pytest.mark.asyncio
@patch("vanta.memory.indexer.ChromaStore")
@patch("vanta.memory.indexer.GraphStore")
async def test_indexer_run(mock_graph_class, mock_chroma_class):
    indexer = Indexer(project_root=".")
    # Mocking out the actual filesystem walk to avoid indexing the real project during unit tests
    indexer.index_file = MagicMock()
    with patch("vanta.memory.indexer.Path.rglob", return_value=[]):
        stats = await indexer.run()
        assert "files" in stats
        assert "chunks" in stats
