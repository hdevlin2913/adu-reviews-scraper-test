from typing import List, Optional, Union

from pydantic import ConfigDict, Field

from src.schemas.base import SnakeCaseAliasMixin


class AddressCountry(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None


class PostalAddress(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    street_address: Optional[str] = None
    address_locality: Optional[str] = None
    postal_code: Optional[str] = None
    address_country: Optional[Union[AddressCountry, str]] = None


class AggregateRating(SnakeCaseAliasMixin):
    type: Optional[str] = Field(None, alias="@type")
    rating_value: Optional[str] = None
    review_count: Optional[int] = None


class BasicData(SnakeCaseAliasMixin):
    context: Optional[str] = Field(None, alias="@context")
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None
    url: Optional[str] = None
    price_range: Optional[str] = None
    aggregate_rating: Optional[AggregateRating] = None
    address: Optional[PostalAddress] = None
    image: Optional[str] = None


class Review(SnakeCaseAliasMixin):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    text: Optional[str] = None
    rate: Optional[str] = None
    trip_date: Optional[str] = None


class PlaceSchema(SnakeCaseAliasMixin):
    model_config = ConfigDict(populate_by_name=True)

    basic_data: Optional[BasicData] = None
    description: Optional[str] = None
    features: Optional[List[str]] = None
    reviews: Optional[List[Review]] = None
