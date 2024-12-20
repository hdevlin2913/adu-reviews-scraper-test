from src.schemas.base import SnakeCaseAliasMixin


class SearchSchema(SnakeCaseAliasMixin):
    name: str
    url: str
