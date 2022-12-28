import pandas as pd
import requests
import json
import time
from tqdm import tqdm


def get_items_per_region(
    user_city,
    user_province,
    user_region,
    user_postal_code,
    lat,
    long,
    country_code="ES",
    dist=10000,
    sleep=None,
    max_items=None,
):

    """Get items for a given region.
    Args:
    - user_city: city name
    - user_province: province name
    - user_region: region name
    - user_postal_code: postal code
    - lat: latitude
    - long: longitude
    - country_code: country code (default: ES)
    - distance: distance in meters (default: 10000)
    - sleep: sleep time in seconds (default: None)
    - max_pages: max number of pages to scrap (default: None)

    Returns:
    - total_df: dataframe with all the items
    """

    total_df = pd.DataFrame()
    items_idx = 0

    # During first item, we will make a different request
    url = (
        f"https://api.wallapop.com/api/v3/general/search?filters_source=quick_filters"
        f"&latitude={lat}&longitude={long}&distance={dist}"
    )

    try:
        response = requests.get(url)  # Get the response
        headers = response.headers  # Get the headers
        data = json.loads(response.text)  # Transform response into a json object
    except:
        print("Error getting first page.")
        return None

    # Get wallapop search id
    search_id = headers["x-wallapop-search-id"]
    items_idx = 40

    # Iterate over first 40 items
    items_list = data["search_objects"]

    # Add data to a dataframe
    total_df = pd.DataFrame(items_list)
    total_df["user_id"] = total_df["user"].apply(lambda x: x["id"])
    total_df = total_df[
        [
            "title",
            "description",
            "distance",
            "user_id",
            "category_id",
            "price",
            "creation_date",
            "modification_date",
        ]
    ]

    # Iterate until we catch an exception
    with tqdm() as pbar:
        while True:

            url = (
                f"https://api.wallapop.com/api/v3/general/search?user_province={user_province}"
                f"&distance={dist}&latitude={lat}&start={items_idx}&user_region={user_region}"
                f"&user_city={user_city}&search_id={search_id}&country_code={country_code}"
                f"&user_postal_code={user_postal_code}&items_count={items_idx}&density_type=20"
                f"&filters_source=quick_filters&order_by=closest&step=0&longitude={long}"
            )

            try:
                response = requests.get(url)  # Get the response
                data = json.loads(
                    response.text
                )  # Transform response into a json object
            except:
                break

            # Per page idx, get search results
            items_list = data["search_objects"]
            if items_list is None:
                break

            # Add data to a dataframe
            try:
                df = pd.DataFrame(items_list)
                df["user_id"] = df["user"].apply(lambda x: x["id"])
                df = df[
                    [
                        "title",
                        "description",
                        "distance",
                        "user_id",
                        "category_id",
                        "price",
                        "creation_date",
                        "modification_date",
                    ]
                ]
            except:
                break

            total_df = total_df.append(df, ignore_index=True)

            items_idx += 40
            if max_items and items_idx > max_items:
                break

            # Add sleep time (in seconds)
            if sleep:
                time.sleep(sleep)

            # Update progress bar
            pbar.update(1)

    # print('Total items scrapped: ', items_idx)
    return total_df


def get_user_info(user_id):
    """Get user info for a certain user id."""

    url = f"https://api.wallapop.com/api/v3/users/{user_id}?language=es_ES"

    try:
        response = requests.get(url).text  # Get the response
        data = json.loads(response)  # Transform response into a json object
    except:
        return None

    try:
        user_alias = data["micro_name"]
        user_gender = data["gender"]
        register_date = data["register_date"]
        user_postal_code = data["location"]["zip"]
        user_city = data["location"]["city"]
        web_slug = data["web_slug"]
        id = data["id"]
        user_url = f"https://es.wallapop.com/app/user/{web_slug}-{id}/published"

    except Exception as e:
        print(e)
        print(data)
        return None

    return {
        "user_alias": user_alias,
        "user_gender": user_gender,
        "register_date": register_date,
        "user_postal_code": user_postal_code,
        "user_city": user_city,
        "user_url": user_url,
    }


def get_user_items(user_id):
    """Get user items for a certain user id."""

    url = f"https://api.wallapop.com/api/v3/users/{user_id}/items"

    try:
        response = requests.get(url).text  # Get the response
        data = json.loads(response)  # Transform response into a json object
    except:
        return None

    try:
        items_list = data["data"]
    except:
        return None

    items_info = {}
    for item in items_list:
        try:
            obj_id = item["id"]

            new_item = {
                "title": item["title"],
                "description": item["description"],
                "category_id": item["category_id"],
                "price": item["price"]["amount"],
            }
        except:
            continue

        items_info[obj_id] = new_item

    return items_info


def get_user_sold_items(user_id):
    """Function to get some of the items that a user has selled.

    Limitation: Only retrieves items that have an opinion when sold them
    Limitation: Only retrieves last 34 items with opininions
    """

    url = f"https://api.wallapop.com/api/v3/users/{user_id}/reviews?init=0"

    try:
        response = requests.get(url)  # Get the response
        items_list = json.loads(response.text)  # Transform response into a json object
    except:
        return None

    user_sold_items = []
    for item in items_list:
        item_type = item["type"]

        if item_type == "sell":
            item_data = item["item"]

            try:
                new_item = {
                    "title": item_data["title"],
                    "category_id": item_data["category_id"],
                    "user_id": user_id,
                    "description": None,
                    "distance": None,
                    "price": None,
                    "creation_date": None,
                    "modification_date": None,
                }
                user_sold_items.append(new_item)

            except:
                continue

    return user_sold_items
