import pytest

from qtp import generate_request


def test_generate_request_single() -> None:
    body = "hihi"
    request = generate_request(body)

    assert request.get("Records", [{}])[0].get("body") == body

def test_generate_request_empty() -> None:
    request = generate_request()
    expected = {"Records": []}

    assert request == expected

def test_generate_request_invalid_type() -> None:
    with pytest.raises(TypeError):
        generate_request(32)
