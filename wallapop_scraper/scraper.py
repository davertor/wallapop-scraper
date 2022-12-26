import pandas as pd
import requests
import json
import time
from tqdm import tqdm



def get_items_per_region(user_city, user_province, user_region, user_postal_code,
                        lat, long, country_code='ES', distance=10000, sleep=None,
                        max_pages=None):
    
    '''Get items for a given region.
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
    '''
    
    total_df = pd.DataFrame()
    page_idx = 0
    
    # Iterate until we catch an exception
    with tqdm() as pbar:
        while True:
        
            url = f'https://api.wallapop.com/api/v3/general/search?user_province={user_province}' \
                f'&distance={distance}&latitude={lat}&start={page_idx}&user_region={user_region}' \
                f'&user_city={user_city}&search_id=d581a483-e79f-4bac-acef-70a0832f0e1b' \
                f'&country_code={country_code}&user_postal_code={user_postal_code}' \
                f'&experiment=reserved_items_baseline&items_count=400&density_type=100' \
                f'&filters_source=default_filters&order_by=oldest&step=0&longitude={long}'
                
            try:
                response = requests.get(url).text  # Get the response
                data = json.loads(response)  # Transform response into a json object
            except:
                break
            
            # Per page idx, get search results
            items_list = data['search_objects']
            if items_list is None:
                break
            
            # Add data to a dataframe
            df = pd.DataFrame(items_list)
            df['user_id'] = df['user'].apply(lambda x: x['id'])
            
            # Check if df is empty
            if total_df.empty:
                total_df = df.copy()
            else:
                total_df = total_df.append(df, ignore_index=True)
                
            page_idx += 1
            if max_pages and page_idx > max_pages:
                break
            
            # Add sleep time (in seconds)
            if sleep:
                time.sleep(sleep)
            
            # Update progress bar
            pbar.update(1)
        
    print('Total pages scrapped: ', page_idx)
    return total_df


def get_user_info(user_id):
    ''' Get user info for a certain user id.'''
    
    url = f'https://api.wallapop.com/api/v3/users/{user_id}?language=es_ES'
    
    try:
        response = requests.get(url).text  # Get the response
        data = json.loads(response)  # Transform response into a json object
    except:
        return None
        
    user_alias = data['micro_name']
    user_gender = data['user_gender']
    register_date = data['register_date']
    user_postal_code = data['location']['zip']
    user_city = data['location']['city']
    
    return {
        'user_alias': user_alias,
        'user_gender': user_gender,
        'register_date': register_date,
        'user_postal_code': user_postal_code,
        'user_city': user_city,
    }
    
    
def get_user_items(user_id):
    ''' Get user items for a certain user id.'''
    
    url = f'https://api.wallapop.com/api/v3/users/{user_id}/items'
    
    try:
        response = requests.get(url).text  # Get the response
        data = json.loads(response)  # Transform response into a json object
    except:
        return None
    
    try:
        items_list = data['data']
    except:
        return None
    
    items_info = {}
    for item in items_list:
        try:
            obj_id = item['id']
            
            new_item = {
                'title': item['title'],
                'description': item['description'],
                'category_id': item['category_id'],
                'price': item['price']['amount'],
            }
        except:
            continue
            
        items_info[obj_id] = new_item
    
    return items_info

        
    