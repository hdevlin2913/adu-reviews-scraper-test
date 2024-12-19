from pydantic import BaseModel, model_validator


class SearchSchema(BaseModel):
    name: str
    url: str

    @model_validator(mode="after")
    def validate_url(self) -> "SearchSchema":
        if "vn" not in self.url:
            self.url = self.url.replace(".com", ".com.vn")

        return self
