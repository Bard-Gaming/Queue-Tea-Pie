from .base import SQSBaseModel
from .event_record import SQSEventRecord


class SQSEventData(SQSBaseModel):
    Records: list[SQSEventRecord]
