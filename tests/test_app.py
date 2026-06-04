"""
Tests for the Mergington High School API
Using AAA (Arrange-Act-Assert) testing pattern
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self):
        """Should return all activities with correct structure"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert isinstance(activities, dict)
        for activity in expected_activities:
            assert activity in activities

    def test_get_activities_has_required_fields(self):
        """Should return activities with all required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        activities = response.json()
        activity = activities["Chess Club"]

        # Assert
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_adds_student_to_activity(self):
        """Should successfully add a student to an activity"""
        # Arrange
        email = "newstudent@example.com"
        activity_name = "Soccer Team"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_signup_prevents_duplicate_registration(self):
        """Should reject attempts to register the same student twice"""
        # Arrange
        email = "duplicate@example.com"
        activity_name = "Chess Club"

        # Act
        response1 = client.post(f"/activities/{activity_name}/signup?email={email}")
        response2 = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400
        error_data = response2.json()
        assert "already signed up" in error_data["detail"]

    def test_signup_fails_for_nonexistent_activity(self):
        """Should return 404 when activity does not exist"""
        # Arrange
        email = "test@example.com"
        activity_name = "NonExistentActivity"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_signup_persists_participant_in_database(self):
        """Should verify participant appears in subsequent activity queries"""
        # Arrange
        email = "persistent@example.com"
        activity_name = "Yoga Club"

        # Act
        client.post(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email in activities[activity_name]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/signup endpoint"""

    def test_remove_participant_unregisters_student(self):
        """Should successfully remove a student from an activity"""
        # Arrange
        email = "toremove@example.com"
        activity_name = "Art Workshop"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert email in data["message"]
        assert activity_name in data["message"]

    def test_remove_participant_fails_if_not_registered(self):
        """Should return 400 when removing a student not signed up"""
        # Arrange
        email = "notregistered@example.com"
        activity_name = "Math Olympiad"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"]

    def test_remove_participant_fails_for_nonexistent_activity(self):
        """Should return 404 when activity does not exist"""
        # Arrange
        email = "test@example.com"
        activity_name = "NonExistentActivity"

        # Act
        response = client.delete(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]

    def test_remove_participant_deletes_from_database(self):
        """Should verify participant is removed from subsequent activity queries"""
        # Arrange
        email = "toremove_persistent@example.com"
        activity_name = "Science Debate"
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        client.delete(f"/activities/{activity_name}/signup?email={email}")
        response = client.get("/activities")

        # Assert
        activities = response.json()
        assert email not in activities[activity_name]["participants"]
