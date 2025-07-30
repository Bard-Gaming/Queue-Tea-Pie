from unittest import TestCase

from qtp import sqs_handler, SQSEventHandler, generate_request
from qtp.models import SQSEventRecord


def test_decorator_handler() -> None:
    handler = sqs_handler()
    assert (
        issubclass(handler._handler, SQSEventHandler),
        "'handler._handler' is not a subclass of 'SQSEventHandler'"
    )

    is_called = False
    def process(record: SQSEventRecord) -> None:
        nonlocal is_called
        is_called = True

    handler.process(process)
    handler._handler(generate_request("a")).process_record("a")  # NOQA -- check if process_record() calls process()

    assert is_called


def test_process() -> None:
    handler = sqs_handler()
    process = lambda *args: None

    assert handler.process(process) is handler
    assert handler._record_processor is process


def test_cleanup() -> None:
    handler = sqs_handler()
    cleanup = lambda *args: None

    assert handler.cleanup(cleanup) is handler
    assert handler._record_cleanup is cleanup
