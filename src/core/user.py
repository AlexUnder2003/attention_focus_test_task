from typing import Annotated

from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.core.db import get_async_session
from src.models.user import User
from src.schemas.user import UserCreate


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_async_session)],
):
    yield SQLAlchemyUserDatabase(session, User)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.secret,
        lifetime_seconds=3600,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    async def validate_password(
        self,
        password: str,
        user: UserCreate | User,
    ) -> None:
        if len(password) < 3:
            raise InvalidPasswordException(
                reason="Пароль должен содержать не менее 3 символов"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Пароль не может содержать ваш email"
            )

    async def on_after_register(
        self,
        user: User,
        request: Request | None = None,
    ):
        print(f"Пользователь {user.email} зарегистрирован.")


async def get_user_manager(
    user_db=Depends(get_user_db),
):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
