from uuid import uuid4


def generate_request(*bodies: str) -> dict:
    """
    Generates a request that has the same format as the
    requests SQS queues send. The bodies of the individual
    messages will be filled with the given bodies, meaning
    there will be as many messages within the request as
    given bodies.
    """
    return {
        "Records": [
            {"messageId": str(uuid4()), "body": body}
            for body in bodies
        ]
    }