from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AddressCountry(BaseModel):
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None


class PostalAddress(BaseModel):
    type: Optional[str] = Field(None, alias="@type")
    street_address: Optional[str] = Field(None, alias="streetAddress")
    address_locality: Optional[str] = Field(None, alias="addressLocality")
    postal_code: Optional[str] = Field(None, alias="postalCode")
    address_country: Optional[AddressCountry] = Field(None, alias="addressCountry")


class AggregateRating(BaseModel):
    type: Optional[str] = Field(None, alias="@type")
    rating_value: Optional[str] = Field(None, alias="ratingValue")
    review_count: Optional[int] = Field(None, alias="reviewCount")


class BasicData(BaseModel):
    context: Optional[str] = Field(None, alias="@context")
    type: Optional[str] = Field(None, alias="@type")
    name: Optional[str] = None
    url: Optional[str] = None
    price_range: Optional[str] = Field(None, alias="priceRange")
    aggregate_rating: Optional[AggregateRating] = Field(None, alias="aggregateRating")
    address: Optional[PostalAddress] = None
    image: Optional[str] = None


class Review(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: Optional[str] = None
    text: Optional[str] = None
    rate: Optional[str] = None
    trip_date: Optional[str] = Field(None, alias="tripDate")


class PlaceSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    basic_data: Optional[BasicData] = Field(None, alias="basicData")
    description: Optional[str] = None
    features: Optional[List[str]] = None
    reviews: Optional[List[Review]] = None
