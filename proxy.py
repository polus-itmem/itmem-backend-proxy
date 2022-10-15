import httpx

from config import config


def user_microservice(url: str, data: dict, _type: str = 'post'):
    url = config.user_microservice_url + url
    token = config.user_microservice_token.get_secret_value()
    return microservice(_type, url, data, token)


def microservice(_type: str, url: str, data: dict, token: str):
    if _type == 'post':
        return httpx.post(url, json = data, headers = {'key': token})
    else:
        return httpx.get(url, headers = {'key': token})
