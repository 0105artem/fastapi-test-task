from pydantic import BaseModel


class TestResponse(BaseModel):
    elapsed: float
