"""
API endpoint tests using the AAA (Arrange-Act-Assert) pattern.

Arrange: Set up test conditions and data
Act: Call the API endpoint
Assert: Verify the response and side effects
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint"""
    
    def test_root_redirects_to_static_index(self, client):
        """
        Arrange: No setup needed for redirect test
        Act: Make GET request to root
        Assert: Verify redirect to static/index.html
        """
        # Act
        response = client.get("/", follow_redirects=False)
        
        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestGetActivitiesEndpoint:
    """Tests for GET /activities endpoint"""
    
    def test_get_all_activities_returns_expected_structure(self, client):
        """
        Arrange: No setup needed, activities already populated
        Act: Request all activities
        Assert: Verify response contains all activities with correct structure
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(activities_data) == 9
        assert "Chess Club" in activities_data
        assert "Programming Class" in activities_data
        
    def test_get_activities_contains_required_fields(self, client):
        """
        Arrange: No setup needed
        Act: Request activities
        Assert: Verify each activity has required fields
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        for activity_name, activity_details in activities_data.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)
    
    def test_get_activities_shows_current_participants(self, client):
        """
        Arrange: Verify initial state
        Act: Get activities
        Assert: Verify participant lists match expected
        """
        # Act
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert "michael@mergington.edu" in activities_data["Chess Club"]["participants"]
        assert "emma@mergington.edu" in activities_data["Programming Class"]["participants"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant_success(self, client):
        """
        Arrange: Choose non-registered email and valid activity
        Act: Post signup request
        Assert: Verify response and participant added
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "signed up" in response.json()["message"].lower()
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client):
        """
        Arrange: Use already-registered participant
        Act: Attempt duplicate signup
        Assert: Verify 400 error and appropriate message
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already registered
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_nonexistent_activity_fails(self, client):
        """
        Arrange: Use invalid activity name
        Act: Attempt signup for non-existent activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Fake Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_full_activity_fails(self, client):
        """
        Arrange: Create a full activity by filling all spots
        Act: Attempt to signup when activity is full
        Assert: Verify 400 error about capacity
        """
        # Arrange
        activity_name = "Basketball Team"  # Only 1 participant, max 15
        # Fill the activity
        for i in range(14):
            client.post(
                f"/activities/{activity_name}/signup",
                params={"email": f"student{i}@mergington.edu"}
            )
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": "final@mergington.edu"}
        )
        
        # Assert
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()


class TestUnregisterEndpoint:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant_success(self, client):
        """
        Arrange: Choose a registered participant
        Act: Post unregister request
        Assert: Verify participant removed
        """
        # Arrange
        activity_name = "Chess Club"
        email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 200
        assert "unregistered" in response.json()["message"].lower()
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email not in activities_data[activity_name]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client):
        """
        Arrange: Use unregistered email for activity
        Act: Attempt to unregister non-participant
        Assert: Verify 400 error
        """
        # Arrange
        activity_name = "Chess Club"
        email = "notregistered@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_unregister_from_nonexistent_activity_fails(self, client):
        """
        Arrange: Use invalid activity name
        Act: Attempt unregister from non-existent activity
        Assert: Verify 404 error
        """
        # Arrange
        activity_name = "Invalid Activity"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_and_signup_again(self, client):
        """
        Arrange: Register, unregister, and attempt re-register same participant
        Act: Full signup -> unregister -> signup cycle
        Assert: Verify state changes correctly
        """
        # Arrange
        activity_name = "Tennis Club"
        email = "testuser@mergington.edu"
        
        # Act - First signup
        response1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Act - Unregister
        response2 = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Act - Re-signup
        response3 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert - Last signup should succeed
        assert response3.status_code == 200
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert email in activities_data[activity_name]["participants"]


class TestIntegration:
    """Integration tests for multiple operations"""
    
    def test_full_workflow_signup_unregister(self, client):
        """
        Arrange: Setup workflow test data
        Act: Execute signup and unregister operations
        Assert: Verify state at each step
        """
        # Arrange
        activity_name = "Science Club"
        email = "workflow@mergington.edu"
        
        # Act & Assert - Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()[activity_name]["participants"])
        
        # Act & Assert - Signup
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200
        
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count + 1
        
        # Act & Assert - Unregister
        unregister_response = client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": email}
        )
        assert unregister_response.status_code == 200
        
        response = client.get("/activities")
        assert len(response.json()[activity_name]["participants"]) == initial_count
