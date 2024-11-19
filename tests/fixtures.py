from fastapi.testclient import TestClient
import pytest
from sqlmodel import create_engine, Session, SQLModel
from sqlmodel.pool import StaticPool

from app.main import app
from app.dependencies import get_session


@pytest.fixture(name="session")  #
def session_fixture():  #
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override

    yield TestClient(app)
    app.dependency_overrides.clear()
