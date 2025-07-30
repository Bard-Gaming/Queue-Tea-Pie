import abc
import logging
from typing import Type, Any
from pydantic import ValidationError

from .models import SQSEventData, SQSEventRecord
from .exceptions import SQSInvalidEventError


__all__ = ["SQSEventHandler"]


_EXCEPTION_GROUPS = tuple[Type[Exception]]
_DEFAULT_EXCEPTION_GROUPS: _EXCEPTION_GROUPS = (Exception,)


class SQSEventHandler(abc.ABC):
    """
    SQS Event Handler base class.
    This class implements the main logic when treating messages.

    A common usage might be:

    class MyHandler(SQSEventHandler):
        def process_record(record: SQSEventRecord) -> None:
            ...  # process record here

        # optional:
        def cleanup_record(record: SQSEventRecord) -> bool | None:
            ...  # clean up any records that caused errors here

    def lambda_handler(event: dict, context: object) -> dict:
        handler = MyHandler(event)
        handler.process_records()
        return handler.response()


    A utility that greatly simplifies the usage of this class is
    the `sqs_handler` class. For information on how to use it, please
    look up its definition in the package's decorator.py file.
    """

    __slots__ = ("failed_ids", "data", "_exception_groups", "_logger", "__record_data", "__is_processing_record")

    def __init__(
            self,
            event: dict,
            /,
            exception_groups: _EXCEPTION_GROUPS = _DEFAULT_EXCEPTION_GROUPS
    ) -> None:
        try:
            self.data = SQSEventData(**event)
        except ValidationError:
            raise SQSInvalidEventError(event)

        self.failed_ids = set()
        self._exception_groups = exception_groups
        self._logger = logging.getLogger(__name__)

        # record data / state:
        self.__record_data: Any = None
        self.__is_processing_record = False

    @property
    def record_data(self) -> Any:
        return self.__record_data

    @record_data.setter
    def record_data(self, value: Any) -> None:
        if not self.__is_processing_record:
            raise AttributeError(f"Can't set attribute 'state' outside of 'process_record' method")
        self.__record_data = value

    @abc.abstractmethod
    def process_record(self, record: SQSEventRecord) -> None:
        """
        SQS Event Handler record processing method.

        This (required) method is called for every record available
        in the given events.
        If an exception that's part of the defined exception groups is
        raised, this will cause the record to 'fail' and be sent back
        to the SQS queue, after optionally being cleaned up using the
        cleanup_record method.
        If data needs to be passed to the `cleanup_record` method, this
        should be done using the `record_data` property, as it's automatically
        set to None before every record is being treated, as well as having
        some safeguards to prevent accidental errors. This is not a requirement
        though, and you may define your own attributes.
        """
        pass  # let user define how you should process messages

    def cleanup_record(self, record: SQSEventRecord, error: Exception) -> bool | None:
        """
        SQS Event handler record cleanup method.

        This (optional) method is called when an error occurs whilst
        processing a record.
        If this method doesn't return anything, or returns a falsy value,
        the record will be considered 'failed' and will be added back into
        the SQS queue.
        If this method returns a truthy value, the record won't be added
        back into the queue and will be considered 'successful'.
        """
        pass  # let user define cleanup (default: does nothing)

    def process_records(self) -> None:
        for record in self.data.Records:
            self._logger.info(f"Starting processing of {record !r}")

            error = self._process_record_internal(record)
            if error is None:
                self._logger.info(f"Successfully processed {record !r}")
                continue

            self._logger.error(
                f"Failed to process {record !r}: {error.__class__.__name__}{': ' if str(error) else ''}{error}"
            )

            if not self.cleanup_record(record, error):
                self.failed_ids.add(record.messageId)

    def response(self) -> dict:
        self._logger.info(f"Failed IDs: {'; '.join(m_id[:8] for m_id in self.failed_ids)}")
        return {
            "batchItemFailures": [
                {"itemIdentifier": message_id} for message_id in self.failed_ids
            ]
        }

    def _process_record_internal(self, record: SQSEventRecord) -> Exception | None:
        error = None

        self.__is_processing_record = True
        self.__record_data = None  # reset record state before processing each record
        try:
            self.process_record(record)
        except self._exception_groups as err:
            error = err
        self.__is_processing_record = False

        return error

    def __repr__(self) -> str:
        return f"SQSEventHandler({self.data !r})"