from .base import SQSBaseModel


class SQSEventRecord(SQSBaseModel):
    messageId: str
    body: str

    def __str__(self) -> str:
        return self.messageId

    def __repr__(self) -> str:
        return f"<Message {self.messageId[:8]}>"
