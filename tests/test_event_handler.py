import pytest

from qtp import SQSEventHandler, generate_request
from qtp.models import SQSEventRecord


def test_handler_record_data():
    class TestHandler(SQSEventHandler):
        def process_record(self, record: SQSEventRecord) -> None:
            self.record_data = "test"
            raise ValueError

        def cleanup_record(self, record: SQSEventRecord, error: Exception) -> bool | None:
            with pytest.raises(AttributeError):
                self.record_data = "bob"  # illegal write
            assert self.record_data == "test"

    request = generate_request("test")
    handler = TestHandler(request)
    handler.process_records()


def test_handler_process_record():
    expected = ["a", "b", "c", "d"]
    processed_bodies = []

    class TestHandler(SQSEventHandler):
        def process_record(self, record: SQSEventRecord) -> None:
            processed_bodies.append(record.body)

    request = generate_request(*expected)
    handler = TestHandler(request)
    handler.process_records()

    assert processed_bodies == expected


def test_handler_cleanup_record():
    request = generate_request("type", "normal message", "value", "boom bap", "attribute", "stuff")
    expected = [TypeError, ValueError, AttributeError]
    cleaned_up_errors = []

    class TestHandler(SQSEventHandler):
        def process_record(self, record: SQSEventRecord) -> None:
            if record.body == "type":
                raise TypeError
            elif record.body == "value":
                raise ValueError
            elif record.body == "attribute":
                raise AttributeError

        def cleanup_record(self, record: SQSEventRecord, error: Exception) -> bool | None:
            cleaned_up_errors.append(error)

    handler = TestHandler(request)
    handler.process_records()

    assert len(expected) == len(cleaned_up_errors)
    for error, err_type in zip(cleaned_up_errors, expected):
        assert isinstance(error, err_type)


def test_handler_response():
    expected = {'batchItemFailures': [
        {'itemIdentifier': 'a'}, {'itemIdentifier': 'b'},
        {'itemIdentifier': 'c'}, {'itemIdentifier': 'd'},
    ]}

    class TestHandler(SQSEventHandler):
        def process_record(self, record: SQSEventRecord) -> None:
            record.messageId = record.body
            raise ValueError

    request = generate_request("a", "b", "c", "d")
    handler = TestHandler(request)
    handler.process_records()

    response = handler.response()

    # note: the items returned by .response() aren't ordered, so
    # for the purposes of this test we need to sort them in order
    # to compare them to the expected values.
    failures: list[dict[str, str]] = response["batchItemFailures"]
    failures.sort(key=lambda el: el['itemIdentifier'])

    assert response == expected
