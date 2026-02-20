import secrets
from urllib.parse import quote
from config import SERVER_DOMAIN, REALITY_PUBLIC_KEY, REALITY_SNI, REALITY_SPIDER_X, REALITY_FINGERPRINT, SHARED_SID

def generate_vless_link(uuid: str, remark: str = "VLESS-Bot"):
    port = 4433
    security = "reality"
    transport_type = "tcp"
    
    #  Используем общий SID из настроек, а не генерируем случайный
    short_id = SHARED_SID 
    
    fingerprint = REALITY_FINGERPRINT

    spx_encoded = quote(REALITY_SPIDER_X, safe='')
    
    link = (
        f"vless://{uuid}@{SERVER_DOMAIN}:{port}?"
        f"type={transport_type}&"
        f"security={security}&"
        f"pbk={REALITY_PUBLIC_KEY}&"
        f"fp={fingerprint}&"
        f"sni={REALITY_SNI}&"
        f"sid={short_id}&"
        f"spx={spx_encoded}&"
        f"flow=xtls-rprx-vision"
        f"#{remark}"
    )
    return link
