from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.errors import DatabaseError

from .models import User


async def create_update_user(
    data: dict, sessionmaker: async_sessionmaker[AsyncSession]
) -> None:
    """
    Create or update user data in the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user_id = data["id"]

                user_exists = await session.execute(
                    select(func.count()).select_from(User).filter(User.id == user_id)
                )

                if user_exists.scalar() == 0:
                    user = User(**data)
                    session.add(user)
                else:
                    data.pop("id")

                    if data:
                        await session.execute(
                            update(User).filter(User.id == user_id).values(**data)
                        )
            except Exception as e:
                await session.rollback()
                raise DatabaseError from e


async def get_user_db(
    username: str, sessionmaker: async_sessionmaker[AsyncSession]
) -> dict:
    """
    Get the user using his username from the db.
    """

    async with sessionmaker() as session:
        async with session.begin():
            try:
                user = (
                    await session.execute(
                        select(User).filter(User.username == username)
                    )
                ).scalar_one()
                return user.columns_to_dict()
            except Exception as e:
                raise DatabaseError from e
