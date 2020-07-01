

def test_get_quiz_submit(client):
    response = client.get("/api/v1/quiz_api/submit_quiz")
    # TODO
    print(response.data)
    # data = json.loads(response.data.decode())
    # data = response.json
    assert response.status_code, 200
    # assert data == {
    #     "status": "success",
    #     "message": "Pinged school class"
    # }
