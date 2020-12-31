import pytest
from flaskr.db import get_db


def test_index(client):
    response = client.get('/')
    assert b'QR-Form-App' in response.data

def test_create(client, app):
    assert client.get('/create').status_code == 200
    with app.app_context():
        db = get_db()
        count = db.execute('SELECT COUNT(id) FROM answers').fetchone()[0]
        assert count == 7


pytest.mark.parametrize('path', (
'/create',
'/RN Association/user1@gmail.com',
))

def test_update(client, app):
    client.get('/RN Association/user1@gmail.com')
