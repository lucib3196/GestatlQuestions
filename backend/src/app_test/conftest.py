# Configuration file for test these are global and are the most generif
from pathlib import Path
from pydantic_settings import BaseSettings


class TestConfig(BaseSettings):
    asset_path: Path


test_config = TestConfig(asset_path=Path("./assets").resolve())
if __name__ == "__main__":
    print(test_config)
