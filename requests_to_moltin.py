import os
import requests

from datetime import datetime, timezone

ACCESS_TOKEN = None


def get_token():
    global ACCESS_TOKEN
    if ACCESS_TOKEN is None or datetime.now(timezone.utc).timestamp() >= \
            create_token()['expires']:
        ACCESS_TOKEN = create_token()['access_token']
    return ACCESS_TOKEN


def create_token():
    client_id = os.getenv('CLIENT_ID')
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit',
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()


def get_shop_products():
    access_token = get_token()
    url = 'https://api.moltin.com/v2/products'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    products = response.json()['data']
    return products


def get_product(id):
    access_token = get_token()
    url = 'https://api.moltin.com/v2/products'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(f'{url}/{id}', headers=headers)
    response.raise_for_status()
    product = response.json()['data']
    return product


def get_url_photo(photo_id):
    access_token = get_token()
    url = 'https://api.moltin.com/v2/files'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(f'{url}/{photo_id}', headers=headers)
    response.raise_for_status()
    photo_url = response.json()['data']['link']['href']
    return photo_url


def add_product_to_cart(chat_id, product_id, quantity):
    access_token = get_token()
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    json_data = {
        'data': {
            'id': product_id,
            'type': 'cart_item',
            'quantity': int(quantity),
        },
    }
    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()


def calculate_price(chat_id):
    access_token = get_token()
    url = f'https://api.moltin.com/v2/carts/{chat_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    total_sum = response.json()['data']['meta']['display_price']['with_tax'][
        'formatted']
    return total_sum


def get_cart(chat_id):
    access_token = get_token()
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_products = response.json()
    return cart_products


def delete_product_to_cart(chat_id, product_id):
    access_token = get_token()
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items/{product_id}'
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def add_contact(chat_id, email):
    access_token = get_token()
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': access_token,
    }
    json_data = {
        'data': {
            'type': 'customer',
            'name': str(chat_id),
            'email': email,
            'delivery_details': 'Do NOT leave in a government building'
        },
    }

    response = requests.post(url, headers=headers, json=json_data)
    response.raise_for_status()
    return response.json()
