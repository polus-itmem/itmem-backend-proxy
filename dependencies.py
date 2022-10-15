from __future__ import annotations

from hashlib import sha256
from typing import Union, List

from fastapi import Request, HTTPException, Depends, Cookie, Response
from models import Role
from config import config


def get_user_id(roles: List[Role], request: Request, response: Response) -> int:
    cookies = request.cookies

    role = cookies.get('role')
    user_id = cookies.get('user_id')
    user_auth = cookies.get('user_auth')

    if not (role or user_id or user_auth):
        if Role.un_auth in roles:
            return -1
        else:
            raise HTTPException(status_code = 501, detail = 'Unauthorize')

    try:
        if sha256(((role + config.web_secret.get_secret_value()) + user_id).encode()).hexdigest() == user_auth:
            return int(user_id)
        else:
            response.delete_cookie(key = "role")
            response.delete_cookie(key = "user_id")
            response.delete_cookie(key = "user_auth")
            raise HTTPException(status_code = 501, detail = 'Unauthorize')
    except:
        pass

    response.delete_cookie(key = "role")
    response.delete_cookie(key = "user_id")
    response.delete_cookie(key = "user_auth")
    raise HTTPException(status_code = 501, detail = 'Unauthorize')
