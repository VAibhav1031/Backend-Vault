# to test authorization
#
# First is Authenticatoin--> then Authorization


def test_login(client, auth_headers):
    response = client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
