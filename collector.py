from pydantic import BaseModel, field_validator, ValidationError
import requests
import json
from config import headers, cookies, num_for_output
import os
import time
import asyncio
from datetime import timedelta


def func_time_count(function):
    def wrapped(*args):
        start = time.perf_counter_ns()
        res = function(*args)
        print(timedelta(microseconds=(time.perf_counter_ns() - start)))
        return res
    return wrapped


def reload_func_3_times(function):
    async def wrapped(*args):
        pass

    return wrapped


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


@func_time_count
def get_data():
    if not os.path.exists('data'):
        os.mkdir('data')

    params = {
        'rent_type[]': '2_rooms',
        'order': 'created_at:desc',
        'page': '1',
        'bounds[lb][lat]': '53.67832826520648',
        'bounds[lb][long]': '27.365152809086844',
        'bounds[rt][lat]': '54.124908978529085',
        'bounds[rt][long]': '27.759527091732025',
        'v': '0.7943315165923253',
    }

    session = requests.Session()

    response = session.get('https://r.onliner.by/sdapi/ak.api/search/apartments', params=params, cookies=cookies,
                           headers=headers).json()
    response_ap = response.get("apartments")
    apart_list: list[Apartment] = []
    # print(response_ap)
    try:
        for apart_it in range(num_for_output):
            apartment = Apartment(id=str(response_ap[apart_it].get("id")),
                                  address=response_ap[apart_it].get("location").get("address"),
                                  latlon=" ".join([str(response_ap[apart_it].get("location").get("latitude")),
                                                   str(response_ap[apart_it].get("location").get("longitude"))]),
                                  created_at=response_ap[apart_it].get("created_at"),
                                  price_usd=str(response_ap[apart_it].get("price").get("amount")),
                                  price_byn=str(response_ap[apart_it].get("price").get("converted").get("BYN").get(
                                      "amount")),
                                  url=response_ap[apart_it].get("url"))
            if response_ap[apart_it].get("photo"):
                apartment.photo = response_ap[apart_it].get("photo"),
            apart_list.append(apartment)
    except ValidationError as e:
        print("Validation error raised!", e)
        return -1

    with open("data/1_data.json", "w") as file:
        for apart in apart_list:
            file.write(apart.model_dump_json(indent=4))
            file.write("\n")

def collector():
    get_data()
