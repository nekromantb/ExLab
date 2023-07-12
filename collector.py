from pydantic import ValidationError
import requests
from config import headers, cookies, num_for_output
import os
import time
from datetime import timedelta
from schemas import Apartment
import json


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
                           headers=headers)
    # if response.status_code == 200:
    #     raise Exception
    response_json = response.json()
    response_ap = response_json.get("apartments")
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
            if apartment.address == "":
                apartment.address = response_ap[apart_it].get("location").get("user_address")
            apart_list.append(apartment)
    except ValidationError as e:
        print("Validation error raised!", e)
        return -1

    with open("data/1_data.json", "w") as file:
        apart_list = [i.dict() for i in apart_list]
        json.dump(apart_list, file, indent=4, ensure_ascii=False)

def collector():
    get_data()
