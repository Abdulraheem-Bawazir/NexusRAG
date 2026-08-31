from fastapi.testclient import TestClient

from app.api.app import create_app


def test_root_serves_web_interface() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get("/")

    assert response.status_code == 200

    assert (
        "NexusRAG"
        in response.text
    )

    assert (
        "Private Knowledge Intelligence"
        in response.text
    )


def test_stylesheet_is_served() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get(
        "/static/styles.css"
    )

    assert response.status_code == 200

    assert (
        "--red"
        in response.text
    )


def test_javascript_is_served() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get(
        "/static/app.js"
    )

    assert response.status_code == 200

    assert (
        "/api/v1"
        in response.text
    )


def test_web_interface_links_api_docs() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get("/")

    assert (
        'href="/docs"'
        in response.text
    )