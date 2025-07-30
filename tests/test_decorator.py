from unittest import TestCase

from qtp import sqs_handler, SQSEventHandler, generate_request
from qtp.models import SQSEventRecord


class TestSQSHandlerDecorator(TestCase):
    def test__handler(self):
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

        self.assertTrue(is_called)

    def test_process(self):
        handler = sqs_handler()
        process = lambda *args: None

        self.assertIs(handler.process(process), handler)
        self.assertIs(handler._record_processor, process)

    def test_cleanup(self):
        handler = sqs_handler()
        cleanup = lambda *args: None

        self.assertIs(handler.cleanup(cleanup), handler)
        self.assertIs(handler._record_cleanup, cleanup)
