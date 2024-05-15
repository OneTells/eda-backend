import hashlib
import hmac

from orjson import dumps

from modules.api.core.config.token import secret_token
from modules.api.core.exceptions.token import NotValidToken


class UserToken:

    @staticmethod
    def __get_signature(user_id: int, user_uuid: str) -> str:
        return hmac.new(secret_token.encode(), dumps({'user_id': user_id, 'user_uuid': user_uuid}), hashlib.sha256).hexdigest()

    @staticmethod
    def parse_token(token: str) -> tuple[int, str]:
        data = token.split('.')

        if len(data) != 2:
            raise NotValidToken()

        try:
            user_id = int(data[0])
        except ValueError:
            raise NotValidToken()

        return user_id, data[1]

    @classmethod
    def create(cls, user_id: int, user_uuid: str) -> str:
        return f'{user_id}.{cls.__get_signature(user_id, user_uuid)}'

    @classmethod
    def validate(cls, user_uuid: str, token: str) -> bool:
        try:
            user_id, signature = cls.parse_token(token)
        except NotValidToken:
            return False

        return cls.__get_signature(user_id, user_uuid) == signature
