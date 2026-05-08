"""Unit tests for config loading."""

from vanta.models import VantaConfig
from vanta.config.loader import load_config


def test_default_config():
    config = VantaConfig()
    assert config.language == "python"
    assert config.llm.groq_model == "llama3-70b-8192"
    assert config.memory.enabled is True
    assert config.tui.theme == "classic"
    assert config.agent.max_steps == 50
    assert config.dry_run is False


def test_config_dry_run_override():
    config = VantaConfig(dry_run=True)
    assert config.dry_run is True


def test_config_llm_fields():
    from vanta.models import LLMConfig
    llm = LLMConfig(temperature=0.5, max_tokens=2048)
    assert llm.temperature == 0.5
    assert llm.max_tokens == 2048


def test_config_memory_fields():
    from vanta.models import MemoryConfig
    mem = MemoryConfig(chunk_size=256, chunk_overlap=32)
    assert mem.chunk_size == 256
    assert mem.chunk_overlap == 32


def test_load_config_returns_vantaconfig(tmp_path):
    """load_config returns a VantaConfig even with no vanta.toml."""
    import os
    old = os.getcwd()
    os.chdir(tmp_path)
    try:
        config = load_config()
        assert isinstance(config, VantaConfig)
    finally:
        os.chdir(old)
