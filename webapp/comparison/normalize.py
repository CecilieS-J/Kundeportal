
from .utils import safe_get

def normalize_brevo(data: dict) -> dict:
    return {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "email": data.get("email", ""),
        "customer_no": None,
        "omneo_id": None,
        "sib_id": data.get("sib_id", ""),
        "phone_home": None,
        "phone_mobile": None,
        "phone_business": None
    }


def normalize_external(data: dict) -> dict:
    return {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "email": data.get("email", ""),
        "customer_no": data.get("customer_no", ""),
        "omneo_id": data.get("omneo_id", ""),
        "sib_id": data.get("sib_id", ""),
        "phone_home": data.get("phone_home", ""),
        "phone_mobile": data.get("phone_mobile", ""),
        "phone_business": data.get("phone_business", "")
    }


def normalize_omneo(data: dict) -> dict:
    # udtræk identities
    id_map = {i.get("handle"): i.get("identifier") for i in data.get("identities", [])}
    return {
        "first_name": data.get("first_name", ""),
        "last_name": data.get("last_name", ""),
        "email": data.get("email", ""),
        # sfcc_customer identity som customer_no
        "customer_no": id_map.get("sfcc_customer", None),
        "omneo_id": data.get("id", ""),
        "sib_id": id_map.get("card_pos", None),
        "phone_home": None,
        "phone_mobile": data.get("mobile_phone", ""),
        "phone_business": None
    }


def normalize_sfcc(data: dict) -> dict:
    # Prøv at finde customer-detaljer i flere mulige nøgler
    cust = None
    if "customers" in data:
        arr = data.get("customers")
        if isinstance(arr, list) and arr:
            cust = arr[0]
    if not cust and data.get("data"):
        # OCAPI v24_5 strukturen
        maybe = data["data"].get("customer")
        cust = maybe or data.get("data")
    if not cust:
        cust = data

    # Tjek også custom_attributes for omneo_id
    omneo_attr = safe_get(cust, "custom_attributes", "omneo_id")

    return {
        "first_name": safe_get(cust, "first_name"),
        "last_name": safe_get(cust, "last_name"),
        "email": safe_get(cust, "email"),
        "customer_no": safe_get(cust, "customer_no"),
        "omneo_id": omneo_attr,
        "sib_id": safe_get(cust, "sib_id"),
        "phone_home": safe_get(cust, "phone_home"),
        "phone_mobile": safe_get(cust, "phone_mobile"),
        "phone_business": safe_get(cust, "phone_business")
    }
