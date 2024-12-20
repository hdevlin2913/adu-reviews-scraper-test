from typing import Optional

from pydantic import Field

from src.schemas.base import SnakeCaseAliasMixin


class LocalizedAdditionalNamesSchema(SnakeCaseAliasMixin):
    long_only_hierarchy: Optional[str] = None


class StreetAddressSchema(SnakeCaseAliasMixin):
    street1: Optional[str] = None


class ParentNamesSchema(SnakeCaseAliasMixin):
    long_only_hierarchy_typeahead_v2: Optional[str] = None


class ParentSchema(SnakeCaseAliasMixin):
    names: Optional[ParentNamesSchema] = None


class NaturalParentNamesSchema(SnakeCaseAliasMixin):
    name: Optional[str] = None


class NaturalParentSschema(SnakeCaseAliasMixin):
    names: Optional[NaturalParentNamesSchema] = None
    place_type: Optional[str] = None


class HierarchySchema(SnakeCaseAliasMixin):
    parent_id: Optional[int] = None
    parent: Optional[ParentSchema] = None
    natural_parent_id: Optional[int] = None
    natural_parent: Optional[NaturalParentSschema] = None


class NamesSchema(SnakeCaseAliasMixin):
    long_only_hierarchy_typeahead_v2: Optional[str] = None


class VacationRentalsRouteSchema(SnakeCaseAliasMixin):
    url: Optional[str] = None


class LocationV2Schema(SnakeCaseAliasMixin):
    place_type: Optional[str] = None
    hierarchy: Optional[HierarchySchema] = None
    names: Optional[NamesSchema] = None
    vacation_rentals_route: Optional[VacationRentalsRouteSchema] = None


class PhotoSizeDynamicSchema(SnakeCaseAliasMixin):
    max_width: Optional[int] = None
    max_height: Optional[int] = None
    url_template: Optional[str] = None


class ThumbnailSchema(SnakeCaseAliasMixin):
    photo_size_dynamic: Optional[PhotoSizeDynamicSchema] = None


class LocationSchema(SnakeCaseAliasMixin):
    localized_name: Optional[str] = None
    localized_additional_names: Optional[LocalizedAdditionalNamesSchema] = None
    street_address: Optional[StreetAddressSchema] = None
    location_v2: Optional[LocationV2Schema] = None
    url: Optional[str] = None
    hotels_url: Optional[str] = Field(None, alias="HOTELS_URL")
    attractions_url: Optional[str] = Field(None, alias="ATTRACTIONS_URL")
    restaurants_url: Optional[str] = Field(None, alias="RESTAURANTS_URL")
    place_type: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_geo: Optional[bool] = None
    thumbnail: Optional[ThumbnailSchema] = None
