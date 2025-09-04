# from freezegun import freeze_time
#
#
# @freeze_time("2025-09-03 02:00:00")
# def test_reset_password(client, verify_otp):
#     request = client.post(
#         "/api/auth/reset-password",
#         json={"new_password": "new_fakeness_"},
#         headers={"Authentication": f"Bearer {verify_otp}"},
#     )
#     with freeze_time("2025-09-03 02:10:10"):
#         assert request.status_code == 401
#         assert request.json["errors"]["reason"] == "token expired"


def test_reset_password(client, verify_otp):
    request = client.post(
        "/api/auth/reset-password",
        json={"new_password": "new_fakeness_"},
        headers={"Authentication": f"Bearer {verify_otp}"},
    )
    assert request.status_code == 200
    assert request.json["message"] == "Password created Sucessfully"
