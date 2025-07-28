from pydantic import BaseModel


# This is done here in case the base model
# used throughout this package needs to change.
SQSBaseModel = BaseModel
