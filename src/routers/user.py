from asyncio import to_thread
from fastapi import (
    APIRouter,
    HTTPException
)
from bcrypt import (
    hashpw,
    gensalt
)
from models import (
    User,
    UserRepository,
    CurrentUser,
    GetUser,
    CreateUser,
    UpdateUser
)

user_router = APIRouter(prefix='/user', tags=['user'])

@user_router.get('/', status_code=200)
async def get_user(current_user: CurrentUser) -> GetUser.Response:
    return GetUser.Response.model_validate(current_user.to_dict())

@user_router.post('/', status_code=201)
async def create_user(
    data: CreateUser.Request, user_repo: UserRepository
) -> CreateUser.Response:
    conflict: User|None = await user_repo.find_by(email=data.email)
    if conflict:
        raise HTTPException(status_code=409, detail='Email already taken')
    password_hash_bytes: bytes = await to_thread(
        hashpw, data.password.encode(), gensalt()
    )
    user: User = await user_repo.create(
        email=data.email, name=data.name,
        password_hash=password_hash_bytes.decode()
    )
    return CreateUser.Response(id=user.id)

@user_router.patch('/', status_code=204)
async def update_user(
    data: UpdateUser.Request, user_repo: UserRepository, current_user: CurrentUser
) -> None:
    kwargs: dict = data.model_dump(exclude_none=True)
    if 'password' in kwargs:
        password: str = kwargs.pop('password')
        password_hash_bytes: bytes = await to_thread(
            hashpw, password.encode(), gensalt()
        )
        kwargs['password_hash'] = password_hash_bytes.decode()
    await user_repo.update(current_user, **kwargs)

@user_router.delete('/', status_code=204)
async def delete_user(
    user_repo: UserRepository, current_user: CurrentUser
) -> None:
    await user_repo.delete(current_user)
