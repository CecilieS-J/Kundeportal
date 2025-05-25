
from typing import Dict, Any

from .normalize import (
    normalize_brevo,
    normalize_external,
    normalize_omneo,
    normalize_sfcc
)
from webapp.brevo_service.service import BrevoService
from webapp.external_customer_service.service import CustomerExternalService
from webapp.omneo_service.service import OmneoService
from webapp.sfcc_service.service import SFCCService


def compare_customer_data(identifier: str, identifier_type: str = "email") -> dict:
    """
    Samler, normaliserer og sammenligner kundedata fra Brevo, External, Omneo og SFCC.
    """
    # Services
    brevo_svc = BrevoService()
    ext_svc = CustomerExternalService()
    omni_svc = OmneoService()
    sfcc_svc = SFCCService()

    brevo_raw = {}
    external_raw = {}
    omneo_raw = {}
    sfcc_raw = {}
    not_found = []

    # 1) External først, hvis vi har customer_no eller goodiecard eller sib_id
    params = {}
    if identifier_type == "customer_no":
        params["customer_no"] = identifier
    elif identifier_type == "goodiecard":
        params["goodie_id"] = identifier
    elif identifier_type == "email":
        params["email"] = identifier
    else:
        params["sib_id"] = identifier
    external_raw = ext_svc.fetch_external(**params)
    if not external_raw:
        not_found.append("External")

    # Udled generelle id'er fra ekstern
    email = external_raw.get("email")
    sib_id = external_raw.get("sib_id")
    card_pos = external_raw.get("omneo_id")
    cust_no = external_raw.get("customer_no")

    # 2) Brevo (foretrækker sib_id, så email)
    if sib_id:
        brevo_raw = brevo_svc.fetch_contact(sib_id)
    elif email:
        brevo_raw = brevo_svc.fetch_contact(email)
    if not brevo_raw:
        not_found.append("Brevo")

    # 3) Omneo (foretrækker card_pos, så email)
    if card_pos:
        om_list = omni_svc.fetch_by_card_pos(card_pos)
    elif email:
        om_list = omni_svc.fetch_by_email(email)
    else:
        om_list = []
    omneo_raw = om_list[0] if om_list else {}
    if not omneo_raw:
        not_found.append("Omneo")

    # 4) SFCC (altid customer_no)
    # hvis vi ikke allerede har customer_no, prøv fra Omneo
    sfcc_cust_no = cust_no or normalize_omneo(omneo_raw).get("customer_no")
    if sfcc_cust_no:
        sfcc_raw = sfcc_svc.fetch_customer_by_customer_no(sfcc_cust_no)
    if not sfcc_raw:
        not_found.append("SFCC")

    # Normaliser
    brevo = normalize_brevo(brevo_raw)
    external = normalize_external(external_raw)
    omneo = normalize_omneo(omneo_raw)
    sfcc = normalize_sfcc(sfcc_raw)

    sources: Dict[str, dict] = {
        "Brevo": brevo,
        "External": external,
        "Omneo": omneo,
        "SFCC": sfcc
    }
    fields = [
        "first_name", "last_name", "email", "customer_no",
        "omneo_id", "sib_id", "phone_home", "phone_mobile", "phone_business"
    ]

    combined = {
        f: {sys: src.get(f, "") for sys, src in sources.items()}
        for f in fields
    }
    differences = {
        f: vals for f, vals in combined.items()
        if len({v for v in vals.values() if v}) > 1
    }
    has_data = any(bool(src) for src in sources.values())

    return {
        "all_data": combined,
        "differences": differences,
        "not_found": not_found,
        "identifier": identifier,
        "identifier_type": identifier_type,
        "has_data": has_data
    }
