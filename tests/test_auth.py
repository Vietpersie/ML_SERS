import pytest
from app import create_app
from config import TestingConfig
from models import db


@pytest.fixture
def client():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.drop_all()


def test_login_page(client):
    response = client.get("/auth/login")
    assert response.status_code == 200
