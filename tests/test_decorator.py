from unittest import TestCase

from qtp import sqs_handler, SQSEventHandler
from qtp.models import SQSEventRecord


class TestSQSHandlerDecorator(TestCase):
    def test__handler(self):
        handler = sqs_handler()
        assert (
            issubclass(handler._handler, SQSEventHandler),
            "'handler._handler' is not a subclass of 'SQSEventHandler'"
        )

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
