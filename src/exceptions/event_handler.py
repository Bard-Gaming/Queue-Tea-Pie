__all__ = ["SQSEventHandlerError", "SQSInvalidEventError"]


class SQSEventHandlerError(Exception):
    pass


class SQSInvalidEventError(SQSEventHandlerError):
    def __init__(self, event: dict) -> None:
        self.event = event  # in case someone handling the error might need it
        super().__init__(f"Invalid SQS Event format: {event !r}")
