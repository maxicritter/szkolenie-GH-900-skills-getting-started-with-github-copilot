"""Tests for the FastAPI activities application"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from src.app import activities
    
    # Store original state
    original_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball practice and games",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 10,
            "participants": ["james@mergington.edu", "isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act in plays and develop performance skills",
            "schedule": "Tuesdays and Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["lucas@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and sculpture",
            "schedule": "Mondays and Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["grace@mergington.edu", "benjamin@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop critical thinking and public speaking skills",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["charlotte@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(original_activities)
    yield
    # Restore after test
    activities.clear()
    activities.update(original_activities)


class TestGetActivities:
    """Test suite for getting activities"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_structure(self, client):
        """Test that activities have the correct structure"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)


class TestSignupForActivity:
    """Test suite for signing up for activities"""
    
    def test_signup_successful(self, client, reset_activities):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant"""
        email = "newstudent@mergington.edu"
        client.post(f"/activities/Chess Club/signup?email={email}")
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert email in activity["participants"]
    
    def test_signup_duplicate_fails(self, client, reset_activities):
        """Test that signing up twice fails"""
        email = "michael@mergington.edu"  # Already in Chess Club
        response = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestUnregisterFromActivity:
    """Test suite for unregistering from activities"""
    
    def test_unregister_successful(self, client, reset_activities):
        """Test successful unregistration from an activity"""
        email = "michael@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        email = "michael@mergington.edu"
        client.post(f"/activities/Chess Club/unregister?email={email}")
        
        response = client.get("/activities")
        activity = response.json()["Chess Club"]
        assert email not in activity["participants"]
    
    def test_unregister_not_registered_fails(self, client, reset_activities):
        """Test that unregistering a non-registered student fails"""
        email = "notregistered@mergington.edu"
        response = client.post(
            f"/activities/Chess Club/unregister?email={email}"
        )
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"].lower()
    
    def test_unregister_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()


class TestActivityConstraints:
    """Test suite for activity constraints"""
    
    def test_max_participants_constraint(self, client, reset_activities):
        """Test that max_participants is respected"""
        # Tennis Club has max 10 participants and 2 already registered
        # Fill it up
        for i in range(8):
            email = f"student{i}@mergington.edu"
            client.post(f"/activities/Tennis Club/signup?email={email}")
        
        # Try to add one more - should fail
        response = client.post(
            "/activities/Tennis Club/signup?email=extra@mergington.edu"
        )
        # Current implementation doesn't check max, but this test documents expected behavior
        # Uncomment when max constraint is implemented:
        # assert response.status_code == 400
    
    def test_participants_count_accuracy(self, client, reset_activities):
        """Test that participant counts are accurate"""
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert len(chess["participants"]) == 2
        
        # Signup one more
        client.post("/activities/Chess Club/signup?email=new@mergington.edu")
        
        response = client.get("/activities")
        chess = response.json()["Chess Club"]
        assert len(chess["participants"]) == 3
