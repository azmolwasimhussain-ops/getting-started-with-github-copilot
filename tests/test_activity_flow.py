from pathlib import Path

from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)
STATIC_DIR = Path(__file__).parents[1] / "src" / "static"


def test_registration_rejects_duplicates_and_updates_activity():
    activity_name = "Soccer Club"
    email = "step3.registration@mergington.edu"
    participants = activities[activity_name]["participants"]
    if email in participants:
        participants.remove(email)

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200
    assert email in client.get("/activities").json()[activity_name]["participants"]

    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert duplicate_response.status_code == 400

    participants.remove(email)


def test_unregister_removes_participant_and_validates_errors():
    activity_name = "Soccer Club"
    email = "step3.unregister@mergington.edu"
    participants = activities[activity_name]["participants"]
    if email in participants:
        participants.remove(email)
    participants.append(email)

    unregister_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert unregister_response.status_code == 200
    assert email not in client.get("/activities").json()[activity_name]["participants"]

    missing_response = client.delete(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert missing_response.status_code == 404

    unknown_response = client.delete(
        "/activities/Unknown Activity/signup",
        params={"email": email},
    )
    assert unknown_response.status_code == 404


def test_frontend_renders_participants_with_accessible_remove_buttons():
    app_js = (STATIC_DIR / "app.js").read_text()
    styles_css = (STATIC_DIR / "styles.css").read_text()
    index_html = (STATIC_DIR / "index.html").read_text()

    assert 'Object.entries(activities)' in app_js
    assert 'aria-label="Remove ${escapeAttribute(participant)}' in app_js
    assert 'method: "DELETE"' in app_js
    assert "await fetchActivities();" in app_js
    assert "class=\"participants-list\"" in app_js
    assert "list-style: none;" in styles_css
    assert 'id="activities-list"' in index_html
