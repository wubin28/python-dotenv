import os
import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

REQUIRED_VAR_NAMES = [
    "DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD",
    "BATCH_SIZE", "MAX_RETRIES", "DRY_RUN",
]

@pytest.fixture
def clean_env():
    """Remove required env vars before test; restore original state after."""
    saved = {name: os.environ.pop(name, None) for name in REQUIRED_VAR_NAMES}
    yield
    for name, original_value in saved.items():
        if original_value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = original_value
