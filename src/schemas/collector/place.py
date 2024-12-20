from typing import List, Optional, Union
from urllib.parse import urljoin

from pydantic import ConfigDict, Field, model_validator

from src.schemas.base import SnakeCaseAliasMixin


class AddressCountrySchema(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None


class PostalAddressSchema(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    street_address: Optional[str] = None
    address_locality: Optional[str] = None
    postal_code: Optional[str] = None
    address_country: Optional[Union[AddressCountrySchema, str]] = None


class AggregateRatingSchema(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    rating_value: Optional[str] = None
    review_count: Optional[int] = None


class BasicDataSchema(SnakeCaseAliasMixin):
    context: Optional[str] = Field(None, alias="@context")
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None
    url: Optional[str] = None
    price_range: Optional[str] = None
    aggregate_rating: Optional[AggregateRatingSchema] = None
    address: Optional[PostalAddressSchema] = None
    image: Optional[str] = None

    @model_validator(mode="after")
    def validate_url(self) -> "BasicDataSchema":
        self.url = urljoin("https://www.tripadvisor.com", self.url)
        return self


class ReviewSchema(SnakeCaseAliasMixin):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    text: Optional[str] = None
    rate: Optional[str] = None
    trip_date: Optional[str] = None


class PlaceSchema(SnakeCaseAliasMixin):
    model_config = ConfigDict(populate_by_name=True)

    basic_data: Optional[BasicDataSchema] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    reviews: Optional[List[ReviewSchema]] = None
