"""
Module used for testing simple server module
"""

from fastapi.testclient import TestClient
import pytest
from prometheus_client import REGISTRY

from application.app import app

client = TestClient(app)

class TestSimpleServer:
    """
    TestSimpleServer class for testing SimpleServer
    """
    @pytest.mark.asyncio
    async def read_health_test(self):
        """Tests the health check endpoint"""
        before_healthcheck_call = REGISTRY.get_sample_value('healthcheck_requests_total')
        assert before_healthcheck_call == 0

        response = client.get("health")
        after_healthcheck_call = REGISTRY.get_sample_value('healthcheck_requests_total')

        assert after_healthcheck_call == 1
        assert response.status_code == 200
        assert response.json() == {"health": "ok"}

    @pytest.mark.asyncio
    async def read_main_test(self):
        """Tests the main endpoint"""
        before_main_call = REGISTRY.get_sample_value('main_requests_total')
        assert before_main_call == 0
        
        response = client.get("/")
        after_main_call = REGISTRY.get_sample_value('main_requests_total')

        assert after_main_call == 1
        assert response.status_code == 200
        assert response.json() == {"msg": "Hello World"}
    

    async def read_agur_test(self):
        before_agur_call = REGISTRY.get_sample_value('agur_requests_total')
        assert before_agur_call == 0
        
        response = client.get("/agur")
        after_agur_call = REGISTRY.get_sample_value('agur_requests_total')
        
        assert after_agur_call == 1
        assert response.status_code == 200
        assert response.json() == {"msg": "Agur!!!"}
