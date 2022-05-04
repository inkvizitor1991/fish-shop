import os
import requests

ACCESS_TOKEN = None


def create_token():
    client_id = os.getenv('CLIENT_ID')
    url = 'https://api.moltin.com/oauth/access_token'
    data = {
        'client_id': client_id,
        'grant_type': 'implicit',
    }

    response = requests.post(url, data=data)
    response.raise_for_status()
    global ACCESS_TOKEN
    ACCESS_TOKEN = response.json()['access_token']
    return ACCESS_TOKEN


def get_shop_products():
    access_token = create_token()
    url = 'https://api.moltin.com/v2/products'

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    products = response.json()['data']
    return products


def get_product(id):
    url = 'https://api.moltin.com/v2/products'

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }

    response = requests.get(f'{url}/{id}', headers=headers)
    response.raise_for_status()
    product = response.json()['data']
    return product


def get_url_photo(photo_id):
    url = 'https://api.moltin.com/v2/files'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    response = requests.get(f'{url}/{photo_id}', headers=headers)
    response.raise_for_status()
    photo_url = response.json()['data']['link']['href']
    return photo_url


def add_product_to_cart(chat_id, product_id, quantity):
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items'

    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
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
    url = f'https://api.moltin.com/v2/carts/{chat_id}'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    total_sum = response.json()['data']['meta']['display_price']['with_tax'][
        'formatted']
    return total_sum


def get_cart(chat_id):
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    cart_products = response.json()
    return cart_products


def delete_product_to_cart(chat_id, product_id):
    url = f'https://api.moltin.com/v2/carts/{chat_id}/items/{product_id}'
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }
    response = requests.delete(url, headers=headers)
    response.raise_for_status()


def add_contact(chat_id, email):
    url = 'https://api.moltin.com/v2/customers'
    headers = {
        'Authorization': ACCESS_TOKEN,
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
