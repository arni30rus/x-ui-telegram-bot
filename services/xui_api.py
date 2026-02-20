import httpx
import uuid
import json
import aiosqlite
import config

async def create_user_in_xui(email: str):
    """
    Стабильная версия: Создает клиента через API.
    Требует нажатия "Сохранить" в веб-интерфейсе для работы.
    """
    new_uuid = str(uuid.uuid4())
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
        "Origin": config.XUI_BASE_URL,
        "Referer": f"{config.XUI_BASE_URL}/"
    }

    # 1. Создаем пользователя через post
    async with httpx.AsyncClient(verify=False) as client:
        print("[DEBUG] Логин и создание клиента...")
        login_resp = await client.post(
            f"{config.XUI_BASE_URL}/login",
            json={"username": config.XUI_USERNAME, "password": config.XUI_PASSWORD},
            headers=headers
        )
        
        if login_resp.status_code != 200:
            raise Exception("Ошибка логина")

        if "3x-ui" in client.cookies:
            headers["Cookie"] = f"3x-ui={client.cookies.get('3x-ui')}"

        client_settings = {
            "id": new_uuid,
            "email": email,
            "flow": config.CLIENT_FLOW, 
            "limitIp": 0,
            "totalGB": 0
        }
        
        payload = {
            "id": config.XUI_INBOUND_ID,
            "settings": json.dumps({"clients": [client_settings]})
        }

        add_resp = await client.post(
            f"{config.XUI_BASE_URL}/panel/inbound/addClient",
            json=payload,
            headers=headers
        )

        if add_resp.status_code != 200:
            print(f"Ошибка API: {add_resp.text}")
            raise Exception("Не удалось добавить клиента через API.")

    # 2. Добавляем в статистику (INSERT OR IGNORE чтобы не было дублей)
    try:
        async with aiosqlite.connect(config.XUI_DB_PATH) as db:
            cursor = await db.execute("PRAGMA table_info(client_traffics)")
            columns_info = await cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            insert_cols = ['email', 'enable'] 
            insert_values = [email, 1]
            
            if 'upload' in columns: insert_cols.append('upload'); insert_values.append(0)
            if 'download' in columns: insert_cols.append('download'); insert_values.append(0)
            if 'total' in columns: insert_cols.append('total'); insert_values.append(0)
            if 'up' in columns: insert_cols.append('up'); insert_values.append(0)
            if 'down' in columns: insert_cols.append('down'); insert_values.append(0)
            if 'expiry_time' in columns: insert_cols.append('expiry_time'); insert_values.append(0)
            
            placeholders = ', '.join(['?'] * len(insert_values))
            cols_str = ', '.join(insert_cols)
            
            # ВАЖНО: OR IGNORE предотвратит ошибку, если запись уже существует
            sql = f"INSERT OR IGNORE INTO client_traffics ({cols_str}) VALUES ({placeholders})"
            
            await db.execute(sql, insert_values)
            await db.commit()
            print(f"[DEBUG] Статистика обновлена (или уже была).")
            
    except Exception as e:
        print(f"[WARNING] Ошибка статистики: {e}")

    print("[DEBUG] Готово. Нажмите Сохранить в веб-интерфейсе.")
    return new_uuid
