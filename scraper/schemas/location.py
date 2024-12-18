from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class LocalizedAdditionalNamesSchema(BaseModel):
    long_only_hierarchy: Optional[str] = Field(None, alias="longOnlyHierarchy")


class StreetAddressSchema(BaseModel):
    street1: Optional[str] = Field(None, alias="street1")


class ParentNamesSchema(BaseModel):
    long_only_hierarchy_typeahead_v2: Optional[str] = Field(None, alias="longOnlyHierarchyTypeaheadV2")


class ParentSchema(BaseModel):
    names: Optional[ParentNamesSchema] = None


class NaturalParentNamesSchema(BaseModel):
    name: Optional[str] = None


class NaturalParentSschema(BaseModel):
    names: Optional[NaturalParentNamesSchema] = None
    place_type: Optional[str] = Field(None, alias="placeType")


class HierarchySchema(BaseModel):
    parent_id: Optional[int] = Field(None, alias="parentId")
    parent: Optional[ParentSchema] = None
    natural_parent_id: Optional[int] = Field(None, alias="naturalParentId")
    natural_parent: Optional[NaturalParentSschema] = Field(None, alias="naturalParent")


class NamesSchema(BaseModel):
    long_only_hierarchy_typeahead_v2: Optional[str] = Field(None, alias="longOnlyHierarchyTypeaheadV2")


class VacationRentalsRouteSchema(BaseModel):
    url: Optional[str] = None


class LocationV2Schema(BaseModel):
    place_type: Optional[str] = Field(None, alias="placeType")
    hierarchy: Optional[HierarchySchema] = None
    names: Optional[NamesSchema] = None
    vacation_rentals_route: Optional[VacationRentalsRouteSchema] = Field(None, alias="vacationRentalsRoute")


class PhotoSizeDynamicSchema(BaseModel):
    max_width: Optional[int] = Field(None, alias="maxWidth")
    max_height: Optional[int] = Field(None, alias="maxHeight")
    url_template: Optional[str] = Field(None, alias="urlTemplate")


class ThumbnailSchema(BaseModel):
    photo_size_dynamic: Optional[PhotoSizeDynamicSchema] = Field(None, alias="photoSizeDynamic")


class LocationDataSchema(BaseModel):
    localized_name: Optional[str] = Field(None, alias="localizedName")
    localized_additional_names: Optional[LocalizedAdditionalNamesSchema] = Field(None, alias="localizedAdditionalNames")
    street_address: Optional[StreetAddressSchema] = Field(None, alias="streetAddress")
    location_v2: Optional[LocationV2Schema] = Field(None, alias="locationV2")
    url: Optional[str] = None
    hotels_url: Optional[str] = Field(None, alias="HOTELS_URL")
    attractions_url: Optional[str] = Field(None, alias="ATTRACTIONS_URL")
    restaurants_url: Optional[str] = Field(None, alias="RESTAURANTS_URL")
    place_type: Optional[str] = Field(None, alias="placeType")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_geo: Optional[bool] = Field(None, alias="isGeo")
    thumbnail: Optional[ThumbnailSchema] = None
