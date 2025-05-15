from config import settings
import requests

def get_sfcc_token():
    url = f'{settings.SFCC_BASE_URL}/dw/oauth2/access_token'
    data = { 'grant_type': 'client_credentials' }
    auth = (settings.SFCC_CLIENT_ID, settings.SFCC_CLIENT_SECRET)
    response = requests.post(url, data=data, auth=auth)
    return response.json().get('access_token')

def get_sfcc_customer(customer_id, token):
    url = f'{settings.SFCC_BASE_URL}/s/-/dw/data/v21_3/customers/{customer_id}'
    headers = { 'Authorization': f'Bearer {token}' }
    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None
