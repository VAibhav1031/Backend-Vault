import datetime
import base64
from functools import wraps
from flask import current_app
import jwt
from flask import request
from .error_handler import unauthorized_error, too_many_requests, bad_request
import secrets
from .models import PasswordReset
import logging

logger = logging.getLogger(__name__)


# -----------------
# Generator Tokn
# -----------------


# for the login
def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=1),
    }
    return jwt.encode(payload, key=current_app.config["SECRET_KEY"], algorithm="HS256")


def generate_token_otp(email, user_id, otp):
    payload = {
        "user_id": user_id,
        "email": email,
        "otp": otp,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=1),
    }
    return jwt.encode(payload, key=current_app.config["SECRET_KEY"], algorithm="HS256")


def generate_password_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=10),
    }

    return jwt.encode(payload, key=current_app.config["SECRET_KEY"], algorithm="HS256")


# ----------------
# Decode Token
# ----------------


# for login
def decode_access_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms="HS256"
        )
        if "user_id" in payload:
            return ("ok", payload["user_id"])

    except jwt.ExpiredSignatureError:
        return ("token expired", None)  # token_expired
    except jwt.InvalidTokenError:
        return ("token invalid", None)  # invalid


# you know for thiss password
def decode_reset_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms="HS256"
        )
        if "otp" in payload and "email" in payload:
            return ("ok", (payload["otp"], payload["email"]))

    except jwt.ExpiredSignatureError:
        return ("token expired", None)  # token_expired
    except jwt.InvalidTokenError:
        return ("token invalid", None)  # invalid


def decode_password_reset_token(token):
    try:
        payload = jwt.decode(
            token, current_app.config["SECRET_KEY"], algorithms="HS256"
        )
        if "user_id" in payload and "email" in payload:
            return ("ok", (payload["user_id"], payload["email"]))

    except jwt.ExpiredSignatureError:
        return ("token expired", None)  # token_expired
    except jwt.InvalidTokenError:
        return ("token invalid", None)  # invalid


# -----------------
# Decrators
# ----------------


# Authorization: Bearer <your_jwt_here> the  payload must be this  when it is sent  by the recipients
def token_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Token Error: Token is missing")
            return unauthorized_error(msg="token error", reason="token is missing")

        token = auth_header.split(" ")[1]
        status, data = decode_access_token(token)
        if status == "ok":
            return func(data, *args, **kwargs)
        else:
            logger.error(f"Token Error: {data}")
            return unauthorized_error(msg="token error", reason=status)

    return wrapper


def otp_token_chk(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Token Error: Token is missing")
            return unauthorized_error(msg="token error", reason="token is missing")

        token = auth_header.split(" ")[1]
        # if decode_reset_token(token):
        #
        status, data = decode_reset_token(token)
        logger.info(f"{status}{data}")
        if status == "ok":
            otp, email = data
            return func(otp, email, *args, **kwargs)
        else:
            logger.warning(f"Token Error: {status}")
            return unauthorized_error(msg="token error", reason=status)

    return wrapper


def reset_token_chk(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning("Token Error: Token is missing")
            return unauthorized_error(msg="token error", reason="token is missing")

        token = auth_header.split(" ")[1]
        status, data = decode_password_reset_token(token)
        if status == "ok":
            user_id, email = data

            reset_record = (
                PasswordReset.query.filter_by(user_id=user_id)
                .order_by(PasswordReset.created_at.desc())
                .first()
            )

            if reset_record:
                if reset_record.used:
                    logger.error(
                        f"Password Reset Token already used  for user_id={
                            user_id}"
                    )
                    return bad_request(
                        msg="",
                        reason="This reset token was already used",
                    )

                if reset_record.attempts >= 4:
                    logger.error("Attempt exceeded for the resetting password")
                    return too_many_requests(
                        msg="Attempt Exceeded for the resetting password",
                        reason="You have exceeded maximum allowed attempts. ",
                    )

            logger.warning(f"the attempts value is {reset_record.attempts}")
            return func(user_id, email, *args, **kwargs)
        else:
            logger.warning(f"Token Error: {status}")
            return unauthorized_error(msg="token error", reason=status)

    return wrapper


# ------------------------
# cursor encoder && decoder
# ------------------------


# encrypt the id (currently using base64 encoding )
def cursor_encoder(task_id):
    purity = str(task_id).encode()
    encoded_cursor = base64.b64encode(purity)
    return encoded_cursor


def cursor_decoder(cursor):
    decoding = base64.b64decode(cursor)
    decoded_cursor = decoding.decode()

    return decoded_cursor

    # --------------
    # OTP helper
    # --------------


def otp_generator():
    # zfill is  the padding , which make the result into the required size
    # cause sometime  for  10**6  you get value 68706  which is not even equal to required size
    # so  zfill add padding to  068706  -->  which is good

    return str(secrets.randbelow(10**6)).zfill(6)
