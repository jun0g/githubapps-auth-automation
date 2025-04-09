import time
import jwt
import logging
import requests

# 로그 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", encoding='utf-8')

def generate_jwt(app_id: str, private_key_path: str) -> str:
    now = int(time.time())
    payload = {
        "iat": now,
        "exp": now + 300,
        "iss": app_id
    }

    try:
        with open(private_key_path, "rb") as pem_file:
            signing_key = pem_file.read()
        encoded_jwt = jwt.encode(payload, signing_key, algorithm="RS256")
        logging.info("Success to create JWT")
        return encoded_jwt
    except FileNotFoundError:
        logging.error(f"Couldn't find private key:{private_key_path}. This program will exit.")
        exit(1)

def request_access_token(jwt_token: str, installation_id: str) -> str:
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json"
    }

    try:
        response = requests.post(url, headers=headers)
        response.raise_for_status()

        data = response.json()
        access_token = data.get("token")

        if not access_token:
            logging.error("Fail to request Access Token.")
            logging.error(f"API Response: {data}")

        logging.info("Complete get Access Token")
        return access_token
    except Exception as e:
        logging.error(f"Occurred error while requesting Access Token: \n{e}")

def get_access_token(app_id: str, key_path: str, install_id: str) -> str:
    jwt_token = generate_jwt(app_id, key_path)
    return request_access_token(jwt_token, install_id)
