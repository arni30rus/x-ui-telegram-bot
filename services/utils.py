import secrets
from config import (
    SERVER_DOMAIN, SERVER_PORT, REALITY_PUBLIC_KEY, REALITY_SNI, REALITY_SPIDER_X, 
    REALITY_FINGERPRINT, SHARED_SID, SECURITY_TYPE, CLIENT_FLOW, TLS_ALPN, TLS_SNI
)

def generate_vless_link(uuid: str, remark: str = "VLESS-Bot"):
    port = SERVER_PORT
    transport_type = "tcp"
    fingerprint = REALITY_FINGERPRINT

    # Базовая часть ссылки
    link = f"vless://{uuid}@{SERVER_DOMAIN}:{port}?encryption=none&type={transport_type}&"

    if SECURITY_TYPE == "reality":
        # конфиг для  Reality
        link += f"security=reality&"
        link += f"sni={REALITY_SNI}&fp={fingerprint}&"
        link += f"pbk={REALITY_PUBLIC_KEY}&sid={SHARED_SID}&"
        if REALITY_SPIDER_X:
            link += f"spx={REALITY_SPIDER_X}&"
            
    elif SECURITY_TYPE == "tls":
        # конфиг для TLS
        link += f"security=tls&"
        link += f"sni={TLS_SNI}&fp={fingerprint}&"
        link += f"alpn={TLS_ALPN}&"

    # Добавляем flow
    if CLIENT_FLOW:
        link += f"flow={CLIENT_FLOW}&"

    # Убираем лишний & в конце, если есть, и добавляем хэш
    if link.endswith("&"):
        link = link[:-1]
        
    link += f"#{remark}"
    return link
