import requests

def build_sfcc_base_url(country, instance, site_id, endpoint, api="shop", version="v24_5"):
    if site_id == "LUST":
        url = f"https://sfcc-{instance}.lustcopenhagen.com" if instance != "prd" else "https://www.lustcopenhagen.com"
    else:
        url = f"https://sfcc-{instance}.magasin.{country.lower()}" if instance != "prd" else f"https://www.magasin.{country.lower()}"

    base_url = f"{url}/s/{site_id}/dw/{api}/{version}/{endpoint}"
    return url, base_url

def get_customer(instance, client_id, access_token, country, site_id, customer_id):
    endpoint = "customers"
    site_url, base_url = build_sfcc_base_url(country, instance, site_id, endpoint)
    request_url = f"{base_url}/{customer_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Origin': site_url,
        'Content-Type': 'application/json'
    }

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching customer: {response.status_code} {response.text}")

    return response.json()

def get_customer_lists(instance, client_id, access_token, country, site_id, list_id):
    api = "data"
    endpoint = "customer_lists"
    site_url, base_url = build_sfcc_base_url(country, instance, site_id, endpoint, api)
    request_url = f"{base_url}/{list_id}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Origin': site_url,
        'Content-Type': 'application/json'
    }

    response = requests.get(request_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Error fetching customer list: {response.status_code} {response.text}")

    return response.json()