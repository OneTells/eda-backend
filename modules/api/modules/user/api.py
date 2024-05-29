import hashlib
import hmac

from asyncpg.pgproto.pgproto import UUID
from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse
from sqlalchemy import func

from core.general.models.user import User
from core.modules.database.methods.requests import Select, Insert
from modules.api.core.config.token import secret_token
from modules.api.core.methods.token import UserToken
from modules.api.core.schemes.api import Content
from modules.api.modules.user.schemes import Token

router = APIRouter(prefix='/user', tags=['user'])


@router.post('/')
async def create_user(login: str, password: str):
    is_exist: bool = await (
        Select(func.count())
        .where(User.login == login)
        .fetch_one(model=lambda x: bool(x[0]))
    )

    if is_exist:
        raise HTTPException(status_code=409, detail="User already exists")

    password_hash = hmac.new(secret_token.encode(), password.encode(), hashlib.sha256).hexdigest()

    user_id, user_uuid = await (
        Insert(User)
        .values(login=login, password_hash=password_hash)
        .returning(User.id, User.uuid)
    )

    token = UserToken.create(user_id=user_id, user_uuid=str(user_uuid))
    return ORJSONResponse(content=Content[Token](content=Token(value=token)).model_dump(), status_code=201)


@router.get('/')
async def get_token(login: str, password: str):
    password_hash = hmac.new(secret_token.encode(), password.encode(), hashlib.sha256).hexdigest()

    data: tuple[int, UUID] | None = await (
        Select(User.id, User.uuid)
        .where(User.login == login, User.password_hash == password_hash)
        .fetch_one()
    )

    if data is None:
        raise HTTPException(status_code=403, detail="Login or password is wrong")

    user_id, user_uuid = data

    token = UserToken.create(user_id=user_id, user_uuid=str(user_uuid))
    return ORJSONResponse(content=Content[Token](content=Token(value=token)).model_dump(), status_code=200)
