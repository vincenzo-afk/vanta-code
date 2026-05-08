"""Unit tests for the memory retriever."""
import pytest
from unittest.mock import patch, MagicMock

from vanta.memory.retriever import Retriever
from vanta.config.schema import VantaConfig, MemoryConfig

@pytest.fixture
def mock_config():
    config = VantaConfig()
    config.memory = MemoryConfig(enabled=True)
    return config

@pytest.mark.asyncio
@patch("vanta.memory.retriever.ChromaStore")
@patch("vanta.memory.retriever.GraphStore")
async def test_retriever_query(mock_graph_class, mock_chroma_class, mock_config):
    # Mock chroma results
    mock_chroma = mock_chroma_class.return_value
    mock_chroma.search.return_value = [
        {"id": "doc1", "content": "Test content", "metadata": {"file": "test.py"}, "score": 0.9}
    ]
    
    retriever = Retriever(config=mock_config)
    results = await retriever.query("test query", top_k=1)
    
    assert len(results) == 1
    assert results[0]["file"] == "test.py"
    assert results[0]["content"] == "Test content"
