import logging
from random import randint

from src import sqs_handler
from src.models import SQSEventRecord


@sqs_handler
def lambda_handler(record: SQSEventRecord) -> None:
    if randint(0, 1):
        raise ValueError("Test error")

    print(f"{record.body = }")
    print(f"Successfully processed {record !r}")

@lambda_handler.cleanup
def lambda_handler(record: SQSEventRecord) -> bool | None:
    print(f"Encountered error when processing {record !r}")


# Do a mock lambda execution with a simulated
# SQS event to see how it works:
def mock_lambda_exec() -> None:
    logging.basicConfig(level="INFO")
    simulated_event = {
        "Records": [
            {
                "messageId": "287364872634872364",
                "body": "hi!",
            },
            {
                "messageId": "752836587263875623",
                "body": "cool body"
            },
            {
                "messageId": "976487264872634872",
                "body": "bye!",
            }
        ]
    }
    context = object()

    response = lambda_handler(simulated_event, context)
    print(f"{response = }")


if __name__ == '__main__':
    mock_lambda_exec()
