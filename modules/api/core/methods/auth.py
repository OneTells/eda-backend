from typing import Annotated

from asyncpg.pgproto.pgproto import UUID
from fastapi import HTTPException, Query

from core.general.models.user import User
from core.modules.database.modules.requests.methods import Select
from modules.api.core.exceptions.token import NotValidToken
from modules.api.core.methods.token import UserToken


async def authorization(token: Annotated[str, Query()] = None) -> int | None:
    if token is None:
        return

    user_id, _ = UserToken.parse_token(token)

    user_uuid: UUID = await (
        Select(User.uuid)
        .where(User.id == user_id)
        .fetch_one(model=lambda x: x[0])
    )

    if user_uuid is None:
        raise HTTPException(status_code=403, detail="Invalid token")

    try:
        is_validated = UserToken.validate(str(user_uuid), token)
    except NotValidToken:
        raise HTTPException(status_code=403, detail="Invalid token")

    if not is_validated:
        raise HTTPException(status_code=403, detail="Invalid token")

    return user_id
