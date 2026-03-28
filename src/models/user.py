from typing import Annotated
from uuid import UUID
from os import getenv
from jwt import decode
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidTokenError
)
from pydantic import (
    BaseModel,
    Field
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column
)
from fastapi import (
    HTTPException,
    Depends
)
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials
)
from database import (
    Base,
    Repository,
    get_repository
)

class User(Base):
    __tablename__ = 'users'
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)

UserRepository = Annotated[Repository[User], Depends(get_repository(User))]

http_bearer = HTTPBearer(auto_error=False)

async def get_current_user(
    user_repo: UserRepository, 
    authorization: HTTPAuthorizationCredentials|None = Depends(http_bearer)
) -> User:
    if not authorization:
        raise HTTPException(status_code=401, detail='Header required - Authorization: Bearer JWT')
    try:
        payload = decode(authorization.credentials, getenv('SECRET_KEY'), algorithms=['HS256'])
        sub: str|None = payload.get('sub')
        current_user: User|None = await user_repo.find_by(id=UUID(sub))
    except (ExpiredSignatureError, InvalidTokenError, ValueError):
        raise HTTPException(status_code=401, detail='Token invalid or expired')
    except Exception:
        raise HTTPException(status_code=401, detail='Unexpected error in authorization')
    if not current_user:
        raise HTTPException(status_code=401, detail=f'User {sub} not found')
    return current_user

CurrentUser = Annotated[User, Depends(get_current_user)]

class GetUser:
    class Response(BaseModel):
        id: UUID
        email: str = Field(..., min_length=10, max_length=50, examples=['taro@email.com'])
        name: str = Field(..., min_length=1, max_length=30, examples=['Taro'])

class CreateUser:
    class Request(BaseModel):
        email: str = Field(..., min_length=10, max_length=50, examples=['taro@email.com'])
        password: str = Field(..., min_length=8, max_length=20, examples=['Taro1234'])
        name: str = Field(..., min_length=1, max_length=30, examples=['Taro'])

    class Response(BaseModel):
        id: UUID

class UpdateUser:
    class Request(BaseModel):
        email: str|None = Field(None, min_length=10, max_length=50, examples=['new-taro@email.com'])
        password: str|None = Field(None, min_length=8, max_length=20, examples=['NewTaro1234'])
        name: str|None = Field(None, min_length=1, max_length=30, examples=['NewTaro'])
