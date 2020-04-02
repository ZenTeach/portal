import json

def test_get_quiz_submit(client):
    response = client.get(
        '/api/v1/quiz_api/submit_quiz'
    )

    data = json.loads(response.data.decode())
    assert response.status_code, 200
    assert data == {
        "status": "success",
        "message": "Pinged school class"
    }
