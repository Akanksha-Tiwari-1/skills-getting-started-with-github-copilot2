"""
pytest configuration and shared fixtures.
Uses dependency injection to provide TestClient and fresh app state for each test.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Reset activities state before each test.
    This ensures test isolation - each test gets a fresh copy of the data.
    """
    # Arrange: Store the original state
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
            "description": "Competitive basketball league and practice",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn and play tennis with teammates",
            "schedule": "Saturdays, 10:00 AM - 11:30 AM",
            "max_participants": 12,
            "participants": ["sarah@mergington.edu", "james@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["lucas@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore STEM topics through experiments and projects",
            "schedule": "Wednesdays, 3:30 PM - 4:30 PM",
            "max_participants": 18,
            "participants": ["maya@mergington.edu", "ryan@mergington.edu"]
        },
        "Drama Club": {
            "description": "Perform in school plays and develop acting skills",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 25,
            "participants": ["isabella@mergington.edu"]
        },
        "Art Class": {
            "description": "Explore painting, sculpture, and mixed media",
            "schedule": "Fridays, 3:00 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["lucy@mergington.edu", "noah@mergington.edu"]
        }
    }
    
    # Clear and restore
    activities.clear()
    activities.update(original_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(original_activities)


@pytest.fixture
def client():
    """
    Provide TestClient for making HTTP requests to the app.
    """
    return TestClient(app)
