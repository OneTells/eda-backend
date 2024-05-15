class NotValidToken(Exception):

    def __init__(self) -> None:
        self.message = 'Токен недействителен'

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self.message}>'
