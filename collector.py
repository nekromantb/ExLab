from pydantic import ValidationError
import requests
from config import headers, cookies, num_for_output, room_count
import os
import time
from datetime import timedelta
from schemas import Apartment
import json
from bs4 import BeautifulSoup


def get_phone_and_description_info(ids: str):
    url = "https://r.onliner.by/ak/apartments/"
    headers_pd = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/114.0.0.0 Safari/537.36',
    }
    url_id = url + ids
    r = requests.get(url=url_id, headers=headers_pd)
    soup = BeautifulSoup(r.text, "lxml")
    phone_article = soup.find("li", class_="apartment-info__item_secondary")
    phone = phone_article.text.strip()
    description_article = soup.find("div", class_="apartment-info__sub-line_extended-bottom")
    description = description_article.text.strip()
    return [phone, description]


def room_param(count: list[int]):
    """Generates a query parameter based on the number of rooms needed.
    Allows searching by multiple parameters at the same time"""
    output: list[str] = []
    for number in count:
        if number == 1:
            output.append(''.join([str(number), "_room"]))
        else:
            output.append(''.join([str(number), "_rooms"]))
    return output[0] if len(output) == 1 else output


def func_time_count(function):
    """Computes the execution time of a function"""

    def wrapped(*args):
        start = time.perf_counter_ns()
        res = function(*args)
        print(timedelta(microseconds=(time.perf_counter_ns() - start)))
        return res

    return wrapped


def reload_func_3_times(function):
    """Restarts the function 3 times in case of exit with an exception"""

    def wrapped(*args):
        for iteration in range(2):
            res = function(*args)
            if res != -1:
                break
            time.sleep(1000)
        return res

    return wrapped


@func_time_count
@reload_func_3_times
def get_data():
    """Returns search results based on predefined values from config"""
    if not os.path.exists('data'):
        os.mkdir('data')

    params = {
        'rent_type[]': room_param(room_count),
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
    if response.status_code not in range(200, 299):
        print("Bad status of response!")
        return -1
    else:
        response_json = response.json()
        response_ap = response_json.get("apartments")
        apart_list: list[Apartment] = []
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
                                      url=response_ap[apart_it].get("url"),
                                      owner=response_ap[apart_it].get("contact").get("owner"))
                if response_ap[apart_it].get("photo"):
                    apartment.photo = response_ap[apart_it].get("photo"),
                if apartment.address == "":
                    apartment.address = response_ap[apart_it].get("location").get("user_address")
                phone_desc = get_phone_and_description_info(apartment.id)
                if phone_desc[0]:
                    apartment.phone_number = phone_desc[0]
                if phone_desc[1]:
                    apartment.description = phone_desc[1]
                apart_list.append(apartment)
        except ValidationError as e:
            print("Validation error raised!", e)
            return -1

    with open("data/1_data.json", "w") as file:
        apart_list = [i.dict() for i in apart_list]
        json.dump(apart_list, file, indent=4, ensure_ascii=False)


def collector():
    get_data()
