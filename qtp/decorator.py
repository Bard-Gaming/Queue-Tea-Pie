from typing import Callable, Type

from .event_handler import SQSEventHandler
from .models import SQSEventRecord


__all__ = ["sqs_handler"]


_RECORD_PROCESSOR_FNC = Callable[[SQSEventRecord], None]
_RECORD_CLEANUP_FNC = Callable[[SQSEventRecord], bool | None]

_NOTHING_FNC = lambda *args, **wargs: None


class sqs_handler:  # NOQA (use as function so keep snake-case)
    """
    SQS Lambda Handler decorator class.

    This class is a utility made to use the SQS Event Handler in an easier,
    more familiar way. To accomplish this, this utility has been designed to
    be used in the same way one can use Python's 'property' class.
    A common usage might be:

    @sqs_handler
    def lambda_handler(record: SQSEventRecord) -> None:
        ...  # process record

    @lambda_handler.cleanup
    def lambda_handler(record: SQSEventRecord) -> bool | None:
        ...  # record cleanup


    Alternatively, you may use the handler as follows:


    def lambda_record_process(record: SQSEventRecord) -> None:
        ...  # process record

    def lambda_record_cleanup(record: SQSEventRecord) -> bool | None:
        ...  # record cleanup

    lambda_handler = sqs_handler(lambda_record_process, lambda_cleanup)
    """

    __slots__ = ("_record_processor", "_record_cleanup", "_handler", "__name__")

    def __init__(
            self,
            record_process: _RECORD_PROCESSOR_FNC = None,
            record_cleanup: _RECORD_CLEANUP_FNC = None
    ) -> None:
        self._record_processor = _NOTHING_FNC
        self._record_cleanup = _NOTHING_FNC
        self._handler: Type[SQSEventHandler] | None = None
        self.__name__ = ""

        self._register(record_processor=record_process, record_cleanup=record_cleanup)

    def _register(
            self,
            *,
            record_processor: _RECORD_PROCESSOR_FNC = None,
            record_cleanup: _RECORD_CLEANUP_FNC = None
    ) -> None:
        record_processor = record_processor if record_processor is not None else self._record_processor
        record_cleanup = record_cleanup if record_cleanup is not None else self._record_cleanup
        self._record_processor = record_processor
        self._record_cleanup = record_cleanup
        self.__name__ = self._record_processor.__name__

        class DefaultSQSHandler(SQSEventHandler):
            def process_record(self, record: SQSEventRecord) -> None:
                record_processor(record)

            def cleanup_record(self, record: SQSEventRecord) -> bool | None:
                return record_cleanup(record)

        self._handler = DefaultSQSHandler

    def process(self, fnc: _RECORD_PROCESSOR_FNC) -> "sqs_handler":
        self._register(record_processor=fnc)
        return self

    def cleanup(self, fnc: _RECORD_CLEANUP_FNC) -> "sqs_handler":
        self._register(record_cleanup=fnc)
        return self

    def __call__(self, event: dict, context: object) -> dict:
        handler = self._handler(event)
        handler.process_records()
        return handler.response()

    def __repr__(self) -> str:
        return f"<SQS function {self.__name__} at {hex(id(self))}>"
