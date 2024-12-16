import json
from config import SERVERS


async def add_client(session, server_id: str, client_id: str, email: str, tg_id: str, limit_ip: int, total_gb: int,
                     expiry_time: int, enable: bool, flow: str):
    """
    Добавляет нового клиента на сервер.

    :param session: Объект сессии для выполнения HTTP-запросов.
    :param server_id: Идентификатор сервера, на который добавляется клиент.
    :param client_id: Уникальный идентификатор клиента.
    :param email: Электронная почта клиента (будет преобразована в нижний регистр).
    :param tg_id: Идентификатор клиента в Telegram.
    :param limit_ip: Ограничение по количеству IP-адресов для клиента.
    :param total_gb: Общее количество гигабайт, доступное клиенту.
    :param expiry_time: Время истечения действия клиента (в формате timestamp).
    :param enable: Флаг, указывающий, активен ли клиент.
    :param flow: Тип потока, используемый для клиента.

    :return: Ответ сервера в формате JSON, если клиент успешно добавлен, иначе None.
    """
    api_url = SERVERS[server_id]['API_URL']
    url = f'{api_url}/panel/api/inbounds/addClient'

    email = email.lower()

    client_data = {
        "id": client_id,
        "alterId": 0,
        "email": email,
        "limitIp": limit_ip,
        "totalGB": total_gb,
        "expiryTime": expiry_time,
        "enable": enable,
        "tgId": tg_id,
        "subId": email,
        "flow": flow,
    }

    settings = json.dumps({"clients": [client_data]})

    data = {
        "id": 1,
        "settings": settings
    }

    headers = {
        'Content-Type': 'application/json',
    }

    async with session.post(url, json=data, headers=headers) as response:
        print(f"Запрос на добавление клиента: {data}")
        print(f"Статус ответа: {response.status}")
        response_text = await response.text()
        print(f"Ответ от сервера: {response_text}")

        if response.status == 200:
            print(f"Клиент добавлен: email={email}")
            return await response.json()
        else:
            print(f"Ошибка при добавлении клиента: {response.status}, {response_text}")
            return None


async def extend_client_key(session, server_id: str, tg_id, client_id, email: str, new_expiry_time: int) -> bool:
    """
    Продлевает срок действия ключа клиента.

    :param session: Объект сессии для выполнения HTTP-запросов.
    :param server_id: Идентификатор сервера, на котором находится клиент.
    :param tg_id: Идентификатор клиента в Telegram.
    :param client_id: Уникальный идентификатор клиента.
    :param email: Электронная почта клиента (будет преобразована в нижний регистр).
    :param new_expiry_time: Новое время истечения действия клиента (в формате timestamp).

    :return: True, если ключ успешно продлен, иначе False.
    """
    api_url = SERVERS[server_id]['API_URL']

    async with session.get(f"{api_url}/panel/api/inbounds/getClientTraffics/{email}") as response:
        print(f"GET {response.url} Status: {response.status}")
        response_text = await response.text()
        print(f"GET Response: {response_text}")

        if response.status != 200:
            print(f"Ошибка при получении данных клиента: {response.status} - {response_text}")
            return False

        client_data = (await response.json()).get("obj", {})
        print(client_data)

        if not client_data:
            print("Не удалось получить данные клиента.")
            return False

        current_expiry_time = client_data.get('expiryTime', 0)

        if current_expiry_time == 0:
            current_expiry_time = new_expiry_time

        updated_expiry_time = max(current_expiry_time, new_expiry_time)

        payload = {
            "id": 1,
            "settings": json.dumps({
                "clients": [
                    {
                        "id": client_id,
                        "alterId": 0,
                        "email": email.lower(),
                        "limitIp": 2,
                        "totalGB": 0,
                        "expiryTime": updated_expiry_time,
                        "enable": True,
                        "tgId": tg_id,
                        "subId": email,
                        " flow": "xtls-rprx-vision"
                    }
                ]
            })
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            async with session.post(f"{api_url}/panel/api/inbounds/updateClient/{client_id}", json=payload,
                                    headers=headers) as response:
                print(f"POST {response.url} Status: {response.status}")
                print(f"POST Request Data: {json.dumps(payload, indent=2)}")
                response_text = await response.text()
                print(f"POST Response: {response_text}")

                if response.status == 200:
                    return True
                else:
                    print(f"Ошибка при продлении ключа: {response.status} - {response_text}")
                    return False
        except Exception as e:
            print(f"Ошибка запроса: {e}")
            return False


async def extend_client_key_admin(session, server_id: str, tg_id, client_id: str, email: str,
                                  new_expiry_time: int) -> bool:
    """
    Продлевает срок действия ключа клиента с правами администратора.

    :param session: Объект сессии для выполнения HTTP-запросов.
    :param server_id: Идентификатор сервера, на котором находится клиент.
    :param tg_id: Идентификатор клиента в Telegram.
    :param client_id: Уникальный идентификатор клиента.
    :param email: Электронная почта клиента (будет преобразована в нижний регистр).
    :param new_expiry_time: Новое время истечения действия клиента (в формате timestamp).

    :return: True, если ключ успешно продлен, иначе False.
    """
    api_url = SERVERS[server_id]['API_URL']

    payload = {
        "id": 1,
        "settings": json.dumps({
            "clients": [
                {
                    "id": client_id,
                    "alterId": 0,
                    "email": email.lower(),
                    "limitIp": 2,
                    "totalGB": 0,
                    "expiryTime": new_expiry_time,
                    "enable": True,
                    "tgId": tg_id,
                    "subId": email,
                    "flow": "xtls-rprx-vision"
                }
            ]
        })
    }

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

    try:
        async with session.post(f"{api_url}/panel/api/inbounds/updateClient/{client_id}", json=payload,
                                headers=headers) as response:
            print(f"POST {response.url} Status: {response.status}")
            print(f"POST Request Data: {json.dumps(payload, indent=2)}")
            response_text = await response.text()
            print(f"POST Response: {response_text}")

            if response.status == 200:
                return True
            else:
                print(f"Ошибка при продлении ключа: {response.status} - {response_text}")
                return False
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return False


async def delete_client(session, server_id: str, client_id: str) -> bool:
    """
    Удаляет клиента с сервера.

    :param session: Объект сессии для выполнения HTTP-запросов.
    :param server_id: Идентификатор сервера, с которого удаляется клиент.
    :param client_id: Уникальный идентификатор клиента.

    :return: True, если клиент успешно удален, иначе False.
    """
    api_url = SERVERS[server_id]['API_URL']
    url = f"{api_url}/panel/api/inbounds/1/delClient/{client_id}"
    headers = {
        'Accept': 'application/json'
    }

    try:
        async with session.post(url, headers=headers) as response:
            if response.status == 200:
                return True
            else:
                print(f"Ошибка при удалении клиента: {response.status} - {await response.text()}")
                return False
    except Exception as e:
        print(f"Ошибка запроса: {e}")
        return False