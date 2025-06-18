from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from backend.tests.conftest import client, sample_flashcard_data, test_db


class TestExampleEndpoints:
    """Test cases for example-related endpoints"""

    def test_create_examples_for_nonexistent_flashcard(
        self, client: TestClient, test_db
    ):
        """Test creating examples for a flashcard that doesn't exist"""
        request_data = {"flashcard_id": 999, "count": 2}
        response = client.post("/examples", json=request_data)
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    @patch("backend.main.get_examples_deepseek")
    def test_create_examples_success(
        self, mock_deepseek, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test successfully creating examples for a flashcard"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好，今天天气真好！", "你好，很高兴认识你。"]

        # First create a flashcard
        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples for the flashcard
        request_data = {"flashcard_id": flashcard_id, "count": 2}

        response = client.post("/examples", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "examples" in data
        assert "total" in data
        assert "flashcard_chinese" in data
        assert data["flashcard_chinese"] == sample_flashcard_data["chinese"]
        assert len(data["examples"]) == 2
        assert data["total"] == 2

        # Verify the mock was called with correct parameters
        mock_deepseek.assert_called_once_with(sample_flashcard_data["chinese"], 2)

    def test_get_examples_for_nonexistent_flashcard(self, client: TestClient, test_db):
        """Test getting examples for a flashcard that doesn't exist"""
        response = client.get("/examples?flashcard_id=999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_examples_no_examples_available(
        self, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test getting examples when none are available"""
        # First create a flashcard
        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Try to get examples when none exist
        response = client.get(f"/examples?flashcard_id={flashcard_id}")
        assert response.status_code == 404
        assert "no examples available" in response.json()["detail"].lower()

    @patch("backend.main.get_examples_deepseek")
    def test_get_examples_success(
        self, mock_deepseek, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test successfully getting examples"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好，请问现在几点了？", "你好，我是来自美国的学生。", "你好，这里的食物很好吃。"]

        # First create a flashcard
        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples first
        create_request_data = {"flashcard_id": flashcard_id, "count": 3}

        create_response = client.post("/examples", json=create_request_data)
        assert create_response.status_code == 200

        # Now get the examples
        response = client.get(f"/examples?flashcard_id={flashcard_id}")
        assert response.status_code == 200

        data = response.json()
        assert "examples" in data
        assert "total" in data
        assert "flashcard_chinese" in data
        assert data["flashcard_chinese"] == sample_flashcard_data["chinese"]
        assert len(data["examples"]) == 3
        assert data["total"] == 3

    def test_get_flashcard_with_examples_nonexistent(self, client: TestClient, test_db):
        """Test getting flashcard with examples for nonexistent flashcard"""
        response = client.get("/flashcard-with-example?flashcard_id=999")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_flashcard_with_examples_no_examples(
        self, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test getting flashcard with examples when no examples exist"""
        # First create a flashcard
        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Get flashcard with examples (should return empty examples list)
        response = client.get(f"/flashcard-with-example?flashcard_id={flashcard_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == flashcard_id
        assert data["chinese"] == sample_flashcard_data["chinese"]
        assert data["examples"] == []
        assert data["examples_count"] == 0

    @patch("backend.main.get_examples_deepseek")
    def test_get_flashcard_with_examples_success(
        self, mock_deepseek, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test successfully getting flashcard with examples"""
        # Mock the DeepSeek API response
        mock_deepseek.return_value = ["你好，欢迎来到中国！", "你好，我们可以做朋友吗？"]

        # First create a flashcard
        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        # Create examples first
        create_request_data = {"flashcard_id": flashcard_id, "count": 2}

        create_response = client.post("/examples", json=create_request_data)
        assert create_response.status_code == 200

        # Now get flashcard with examples
        response = client.get(f"/flashcard-with-example?flashcard_id={flashcard_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == flashcard_id
        assert data["chinese"] == sample_flashcard_data["chinese"]
        assert isinstance(data["examples"], list)
        assert data["examples_count"] == 2
        assert len(data["examples"]) == data["examples_count"]
        assert "你好，欢迎来到中国！" in data["examples"]
        assert "你好，我们可以做朋友吗？" in data["examples"]

    @patch("backend.main.get_examples_deepseek")
    def test_create_examples_api_failure(
        self, mock_deepseek, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test handling of DeepSeek API failure"""
        mock_deepseek.side_effect = Exception("API Error")

        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        request_data = {"flashcard_id": flashcard_id, "count": 2}

        response = client.post("/examples", json=request_data)
        assert response.status_code == 500
        assert "Failed to generate examples" in response.json()["detail"]
        assert "API Error" in response.json()["detail"]

    @patch("backend.main.get_examples_deepseek")
    def test_create_examples_empty_response(
        self, mock_deepseek, client: TestClient, test_db, sample_flashcard_data
    ):
        """Test handling when DeepSeek API returns empty list"""
        mock_deepseek.return_value = []

        flashcard_response = client.post("/flashcards", json=sample_flashcard_data)
        assert flashcard_response.status_code == 200
        flashcard_id = flashcard_response.json()["id"]

        request_data = {"flashcard_id": flashcard_id, "count": 2}

        response = client.post("/examples", json=request_data)
        assert response.status_code == 200

        data = response.json()
        assert "examples" in data
        assert "total" in data
        assert data["total"] == 0
        assert len(data["examples"]) == 0
