from pydantic import BaseModel


class SampleEmail(BaseModel):
    subject: str
    message: str
