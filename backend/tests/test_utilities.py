from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.tests.conftest import authenticated_client, client, test_db, test_user


class TestUtilityEndpoints:
    """Test cases for utility endpoints like translate and pinyin"""

    @patch("backend.services.translation_service.translate_google")
    def test_translate_api(
        self, mock_translate, authenticated_client: TestClient, test_db
    ):
        """Test the translation API endpoint"""
        # Mock the translation API response
        mock_translate.return_value = ["Hello", "Hi"]

        request_data = {"chinese": "你好"}

        response = authenticated_client.post("/translate", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "translation" in data
        assert data["translation"] == "Hello"

        # Verify the mock was called with correct parameters
        mock_translate.assert_called_once_with("你好")

    @patch("backend.services.translation_service.translate_google")
    def test_translate_api_invalid_input(
        self, mock_translate, authenticated_client: TestClient, test_db
    ):
        """Test translation API with invalid input"""
        # Mock the translation API to return empty result
        mock_translate.return_value = [""]

        request_data = {"chinese": ""}

        response = authenticated_client.post("/translate", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "translation" in data
        assert data["translation"] == ""

    def test_pinyin_api(self, authenticated_client: TestClient, test_db):
        """Test the pinyin API endpoint"""
        request_data = {"chinese": "你好"}

        response = authenticated_client.post("/pinyin", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "pinyin" in data
        assert isinstance(data["pinyin"], str)
        assert len(data["pinyin"]) > 0

    def test_pinyin_api_multiple_characters(
        self, authenticated_client: TestClient, test_db
    ):
        """Test pinyin API with multiple characters"""
        request_data = {"chinese": "北京大学"}

        response = authenticated_client.post("/pinyin", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "pinyin" in data
        assert isinstance(data["pinyin"], str)
        # Should contain pinyin for multiple characters
        assert len(data["pinyin"]) > len(request_data["chinese"])

    def test_pinyin_api_invalid_input(self, authenticated_client: TestClient, test_db):
        """Test pinyin API with invalid input"""
        request_data = {"chinese": ""}

        response = authenticated_client.post("/pinyin", json=request_data)
        # Should handle empty string gracefully
        assert response.status_code in [200, 422]
