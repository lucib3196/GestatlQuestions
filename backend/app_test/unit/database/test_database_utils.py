import pytest
from uuid import UUID, uuid4
from src.utils.database_utils import *


def test_convert_uuid_passes_uuid():
    random_uuid = uuid4()
    assert convert_uuid(random_uuid) == random_uuid


def test_conver_valid_uuid():
    s = "12345678-1234-5678-1234-567812345678"
    result = convert_uuid(s)
    assert isinstance(result, UUID)
    assert str(result) == s


@pytest.mark.parametrize(
    "bad_input",
    [
        "not-a-uuid",
        "1234",
        1234,  # non-string, non-UUID
        None,  # None should fail
        {"id": "1234"},  # wrong type
    ],
)
def test_bad_uuid_input(bad_input):
    with pytest.raises(ValueError) as exec:
        convert_uuid(bad_input)
    assert "Could not convert" in str(exec.value)
