"""Unit tests for plot tools."""
import pytest
from vanta.tools.plot_tools import plot_data

@pytest.mark.asyncio
async def test_plot_data():
    result = await plot_data(data=[1, 2, 3], chart_type="line", title="Test Line")
    assert isinstance(result, str)
    assert len(result) > 0

@pytest.mark.asyncio
async def test_plot_data_bar():
    result = await plot_data(data=[1, 2, 3], chart_type="bar", title="Test Bar")
    assert isinstance(result, str)
    assert len(result) > 0
