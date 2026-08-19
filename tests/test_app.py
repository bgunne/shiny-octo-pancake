def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_seeded_activity_data(client):
    # Arrange
    expected_participants = [
        "michael@mergington.edu",
        "daniel@mergington.edu",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert "Chess Club" in response.json()
    assert response.json()["Chess Club"]["max_participants"] == 12
    assert response.json()["Chess Club"]["participants"] == expected_participants


def test_signup_adds_student_to_activity(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Signed up {email} for {activity_name}"
    }
    assert email in client.get("/activities").json()[activity_name]["participants"]


def test_signup_rejects_duplicate_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    initial_participants = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student already signed up for this activity"
    }
    assert client.get("/activities").json()[activity_name]["participants"] == initial_participants


def test_signup_rejects_unknown_activity(client):
    # Arrange
    email = "alex@mergington.edu"

    # Act
    response = client.post(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_signup_requires_email(client):
    # Arrange
    activity_name = "Soccer Club"

    # Act
    response = client.post(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_unregister_removes_existing_student(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {
        "message": f"Unregistered {email} from {activity_name}"
    }
    assert email not in client.get("/activities").json()[activity_name]["participants"]


def test_unregister_rejects_unknown_activity(client):
    # Arrange
    email = "alex@mergington.edu"

    # Act
    response = client.delete(
        "/activities/Unknown Club/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_rejects_student_not_signed_up(client):
    # Arrange
    activity_name = "Soccer Club"
    email = "alex@mergington.edu"
    initial_participants = client.get("/activities").json()[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }
    assert client.get("/activities").json()[activity_name]["participants"] == initial_participants


def test_unregister_requires_email(client):
    # Arrange
    activity_name = "Soccer Club"

    # Act
    response = client.delete(f"/activities/{activity_name}/signup")

    # Assert
    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"] == ["query", "email"]


def test_signup_and_unregister_workflow_updates_activity_listing(client):
    # Arrange
    activity_name = "Art Club"
    email = "alex+art@mergington.edu"

    # Act
    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    listed_after_signup = client.get("/activities").json()
    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    listed_after_unregister = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert email in listed_after_signup[activity_name]["participants"]
    assert unregister_response.status_code == 200
    assert email not in listed_after_unregister[activity_name]["participants"]