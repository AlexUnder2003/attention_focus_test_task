import pytest_asyncio
from httpx import AsyncClient
from httpx._transports.asgi import ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

from src.core.db import Base, get_async_session
from src.core.user import current_user
from src.main import app
from src.models.task import Task, TaskStatus

app.dependency_overrides[current_user] = lambda: {
    "id": 1,
    "email": "test@example.com",
}


@pytest_asyncio.fixture(scope="session")
async def engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    async_session = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession):
    async def override_get_session():
        yield db_session

    app.dependency_overrides[get_async_session] = override_get_session

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as client:
        yield client

    app.dependency_overrides.pop(get_async_session, None)


@pytest_asyncio.fixture
async def test_task(db_session: AsyncSession):
    task = Task(
        title="Test Task",
        description="Test Desc",
        status=TaskStatus.PENDING,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_task_with_status(db_session: AsyncSession):
    task = Task(
        title="Test Task with Status",
        description="Test Desc with Status",
        status=TaskStatus.DONE,
    )
    db_session.add(task)
    await db_session.flush()
    await db_session.refresh(task)
    return task


@pytest_asyncio.fixture
async def test_tasks(db_session: AsyncSession):
    tasks = [
        Task(title="Task 1", description="Desc 1", status=TaskStatus.PENDING),
        Task(
            title="Task 2", description="Desc 2", status=TaskStatus.IN_PROGRESS
        ),
        Task(title="Task 3", description="Desc 3", status=TaskStatus.DONE),
    ]
    db_session.add_all(tasks)
    await db_session.flush()
    for task in tasks:
        await db_session.refresh(task)

    return {str(i + 1): task for i, task in enumerate(tasks)}
