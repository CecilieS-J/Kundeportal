def safe_get(data: dict, *keys, default="") -> str:
    """
    Sikkert opslag i nested dictionary.

    Eksempel:
        safe_get(obj, "data", "email") svarer til obj["data"]["email"]
        men returnerer "" hvis noget mangler.
    """
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data if data is not None else default


def flatten_profile(profile: dict, field_map: dict) -> dict:
    """
    Konverterer et profil-objekt med forskellige feltnavne til en flad dict
    med ensartede feltnavne, baseret på mapping.

    Eksempel:
        field_map = {"firstName": "first_name", "email": "email"}
    """
    return {std_key: profile.get(sys_key, "") for sys_key, std_key in field_map.items()}
