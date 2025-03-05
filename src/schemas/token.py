from pydantic import BaseModel

__all__ = ["Token", "TokenData"]

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    e_mail: str | None = None