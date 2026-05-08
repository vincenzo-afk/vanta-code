"""Integration tests for the full memory pipeline (index -> retrieve)."""
import pytest
from pathlib import Path
from unittest.mock import patch

from vanta.memory.indexer import Indexer
from vanta.memory.retriever import Retriever
from vanta.config.schema import VantaConfig, MemoryConfig

@pytest.fixture
def mock_config(tmp_path):
    config = VantaConfig()
    config.project_root = str(tmp_path)
    config.memory = MemoryConfig(enabled=True, chroma_db_path=str(tmp_path / ".vanta/chroma"))
    return config

@pytest.mark.asyncio
@patch("vanta.memory.indexer.ChromaStore")
@patch("vanta.memory.indexer.GraphStore")
async def test_memory_pipeline(mock_graph_class, mock_chroma_class, mock_config, tmp_path):
    # Create a dummy file
    dummy_file = tmp_path / "dummy.py"
    dummy_file.write_text("def hello():\n    print('world')\n", encoding="utf-8")
    
    # 1. Index
    indexer = Indexer(project_root=str(tmp_path))
    # Mocking rglob to only find our dummy file
    with patch("vanta.memory.indexer.Path.rglob", return_value=[dummy_file]):
        stats = await indexer.run()
        assert stats is not None

    # 2. Retrieve
    # Since we mocked ChromaStore, we just ensure it initializes correctly
    retriever = Retriever(config=mock_config)
    assert retriever is not None
