import asyncio
from sqlalchemy import select, func
from app.core.database import engine, Base, AsyncSessionLocal
from app.models.user import User


async def create_test_users() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        count_res = await db.execute(select(func.count()).select_from(User))
        count = count_res.scalar_one()
        if count > 0:
            print("Users already exist, skip seeding")
            return

        users = [
            User(name="Иван Иванов", api_key="user1"),
            User(name="Мария Петрова", api_key="user2"),
            User(name="Пётр Сидоров", api_key="user3"),
        ]
        db.add_all(users)
        await db.commit()
        print("Created users: user1, user2, user3")


if __name__ == "__main__":
    asyncio.run(create_test_users())
