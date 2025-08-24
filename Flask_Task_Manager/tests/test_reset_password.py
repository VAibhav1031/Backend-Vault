def test_reset_password(client, verify_otp):
    request = client.post(
        "/api/auth/reset-password",
        json={"new_password": "new_fakeness_"},
        headers={"Authentication": f"Bearer {verify_otp}"},
    )

    assert request.status_code == 200
    assert request.json["message"] == "Password created Sucessfully"
