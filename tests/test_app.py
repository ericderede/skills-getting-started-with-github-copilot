"""Tests for the FastAPI application"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    yield
    # Reset participants for all activities
    from app import activities
    activities["Chess Club"]["participants"] = ["michael@mergington.edu", "daniel@mergington.edu"]
    activities["Programming Class"]["participants"] = ["emma@mergington.edu", "sophia@mergington.edu"]
    activities["Gym Class"]["participants"] = ["john@mergington.edu", "olivia@mergington.edu"]
    activities["Basketball Team"]["participants"] = []
    activities["Soccer Club"]["participants"] = []
    activities["Drama Club"]["participants"] = []
    activities["Art Workshop"]["participants"] = []
    activities["Math Olympiad"]["participants"] = []
    activities["Debate Team"]["participants"] = []


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that get activities endpoint returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that get activities returns a dictionary"""
        response = client.get("/activities")
        data = response.json()
        assert isinstance(data, dict)

    def test_get_activities_contains_chess_club(self, client):
        """Test that activities include Chess Club"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data

    def test_get_activities_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        for activity_name, activity_details in data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details

    def test_get_activities_initial_participants(self, client):
        """Test that Chess Club has initial participants"""
        response = client.get("/activities")
        data = response.json()
        assert len(data["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in data["Chess Club"]["participants"]


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_returns_200(self, client, reset_activities):
        """Test that signup endpoint returns 200 status code"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, reset_activities):
        """Test that signup returns a success message"""
        response = client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]
        assert "Basketball Team" in data["message"]

    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup adds participant to activity"""
        client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "student@mergington.edu" in data["Basketball Team"]["participants"]

    def test_signup_to_nonexistent_activity_returns_404(self, client):
        """Test that signing up to a non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404

    def test_signup_increases_participant_count(self, client, reset_activities):
        """Test that signup increases the participant count"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Basketball Team"]["participants"])

        client.post(
            "/activities/Basketball%20Team/signup?email=student@mergington.edu"
        )

        response_after = client.get("/activities")
        count_after = len(response_after.json()["Basketball Team"]["participants"])

        assert count_after == count_before + 1


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200(self, client, reset_activities):
        """Test that unregister endpoint returns 200 status code"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, reset_activities):
        """Test that unregister returns a success message"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "michael@mergington.edu" in data["message"]

    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister removes participant from activity"""
        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        response = client.get("/activities")
        data = response.json()
        assert "michael@mergington.edu" not in data["Chess Club"]["participants"]

    def test_unregister_decreases_participant_count(self, client, reset_activities):
        """Test that unregister decreases the participant count"""
        response_before = client.get("/activities")
        count_before = len(response_before.json()["Chess Club"]["participants"])

        client.post(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )

        response_after = client.get("/activities")
        count_after = len(response_after.json()["Chess Club"]["participants"])

        assert count_after == count_before - 1

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregistering from a non-existent activity returns 404"""
        response = client.post(
            "/activities/NonExistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404

    def test_unregister_nonexistent_participant_returns_404(self, client, reset_activities):
        """Test that unregistering a non-existent participant returns 404"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 404


class TestRoot:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that root endpoint redirects to static index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
