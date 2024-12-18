from typing import List

from pydantic import BaseModel


class SearchSchema(BaseModel):
    name: str
    url: str
