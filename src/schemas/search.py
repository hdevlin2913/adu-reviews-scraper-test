from pydantic import BaseModel, model_validator


class SearchSchema(BaseModel):
    name: str
    url: str
