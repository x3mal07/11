import pytest
from app import app, load_wishes, save_wishes

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index(client):
    """Тест: главная страница возвращает 200"""
    response = client.get('/')
    assert response.status_code == 200

def test_add_wish(client):
    """Тест: добавление желания"""
    response = client.post('/add', data={
        'name': 'Тестовое желание',
        'price': 1000
    })
    assert response.status_code == 302  # редирект

def test_detail_wish(client):
    """Тест: детальный просмотр"""
    response = client.get('/wish/1')
    # Если желания нет, будет 404
    assert response.status_code in [200, 404]

def test_search(client):
    """Тест: поиск"""
    response = client.get('/search?q=тест')
    assert response.status_code == 200

def test_delete_wish(client):
    """Тест: удаление"""
    response = client.get('/delete/1')
    assert response.status_code in [302, 404]