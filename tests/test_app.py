import pytest
import json
import os
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_home_endpoint(client):
    response = client.get('/')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'ok'
    assert 'pid' in data
    assert 'timestamp' in data


def test_health_endpoint(client):
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['healthy'] is True
    assert 'pid' in data
    assert 'timestamp' in data


def test_compute_endpoint(client):
    response = client.get('/compute')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['result'] == sum(i for i in range(100000))
    assert 'processing_time_ms' in data
    assert data['processing_time_ms'] > 0
    assert 'pid' in data
    assert 'timestamp' in data


def test_info_endpoint(client):
    response = client.get('/info')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['app'] == 'Flask Web Server'
    assert data['version'] == '1.0'
    assert data['purpose'] == 'CPU Contention Analysis'
    assert 'pid' in data
    assert 'timestamp' in data
