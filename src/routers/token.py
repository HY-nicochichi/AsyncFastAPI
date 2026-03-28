from os import getenv
from datetime import timedelta
from jwt import encode
from bcrypt import checkpw
from asyncio import to_thread
from fastapi import (
    APIRouter,
    HTTPException
)
from database import utc_now
from models import (
    CreateToken,
    User,
    UserRepository
)

token_router = APIRouter(prefix='/token', tags=['token'])

@token_router.post('/', status_code=200)
async def create_token(
    data: CreateToken.Request, user_repo: UserRepository
) -> CreateToken.Response:
    user: User|None = await user_repo.find_by(email=data.email)
    if not user:
        raise HTTPException(status_code=401, detail='Incorrect email or password')
    is_correct_password: bool = await to_thread(
        checkpw, data.password.encode(), user.password_hash.encode()
    )
    if not is_correct_password:
        raise HTTPException(status_code=401, detail='Incorrect email or password')
    access_token: str = encode(
        {'sub': str(user.id), 'exp': utc_now() + timedelta(days=7)},
        getenv('SECRET_KEY'), algorithm='HS256'
    )
    return CreateToken.Response(access_token=access_token)
