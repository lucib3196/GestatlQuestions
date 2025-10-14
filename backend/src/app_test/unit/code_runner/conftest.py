from pydantic_settings import BaseSettings
from pathlib import Path
import pytest


class TestConfig(BaseSettings):
    asset_path: Path


test_config = TestConfig(
    asset_path=Path("src/app_test/unit/code_runner/test_assets").resolve()
)


@pytest.fixture
def get_asset_path():
    return test_config.asset_path
