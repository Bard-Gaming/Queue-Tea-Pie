import json

from qtp import sqs_handler, generate_request
from qtp.models import SQSEventRecord


@sqs_handler
def lambda_handler(record: SQSEventRecord) -> None:
    data = json.loads(record.body)
    print(f"Loaded data for user {data.get('user', 'unknown') !r}!")

@lambda_handler.cleanup
def lambda_handler(record: SQSEventRecord, error: Exception) -> bool | None:
    print(f"Failed to process {record} ({error})")


if __name__ == '__main__':
    request = generate_request(
        '{"user": "bob", "age": 32}',
        "This is an invalid request, muhahahaha!"
    )

    lambda_handler(request, object())
