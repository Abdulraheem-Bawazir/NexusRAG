from fastapi.testclient import TestClient

from app.api.app import create_app


def test_request_id_is_added_to_response() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    request_id = response.headers.get(
        "X-Request-ID"
    )

    assert request_id
    assert isinstance(
        request_id,
        str,
    )


def test_existing_request_id_is_preserved() -> None:
    client = TestClient(
        create_app()
    )

    response = client.get(
        "/health",
        headers={
            "X-Request-ID": (
                "nexusrag-test-request"
            )
        },
    )

    assert response.status_code == 200

    assert (
        response.headers[
            "X-Request-ID"
        ]
        == "nexusrag-test-request"
    )