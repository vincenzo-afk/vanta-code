"""Config management package."""
from vanta.config.loader import load_config
from vanta.config.schema import VantaConfig

__all__ = ["load_config", "VantaConfig"]
