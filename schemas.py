from pydantic import BaseModel, field_validator, ValidationError


class Apartment(BaseModel):
    id: str
    created_at: str
    latlon: str
    photo: str | None = None
    address: str
    price_usd: str
    price_byn: str
    url: str
    phone_number: str | None = None
    description: str | None = None
    owner: bool | None

    @field_validator('id')
    def id_must_be_int(cls, value):
        for c in value:
            if c not in "0123456789":
                raise ValidationError("ID must be integer!")
        return value

    @field_validator('price_usd')
    def price_usd_valid(cls, value):
        for c in value:
            if c not in "0123456789,.":
                raise ValidationError("Price not valid!")
        return value

    @field_validator('price_byn')
    def price_byn_valid(cls, value):
        for c in value:
            if c not in "0123456789,.":
                raise ValidationError("Price not valid!")
        return value
