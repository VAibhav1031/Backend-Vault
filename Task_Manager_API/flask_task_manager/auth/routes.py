from flask import Blueprint, jsonify, request
from flask_task_manager import db
from flask_task_manager.models import User, PasswordReset
from flask import current_app
from flask_task_manager import bcrypt
from flask_task_manager.utils import (
    generate_token,
    generate_token_otp,
    otp_token_chk,
    otp_generator,
    generate_password_token,
    reset_token_chk,
)
from flask_task_manager.error_handler import (
    handle_marshmallow_error,
    not_found,
    user_already_exists,
    unauthorized_error,
    internal_server_error,
    forbidden_access,
    bad_request,
)
from flask_task_manager.schemas import (
    RegisterSchema,
    LoginSchema,
    ValidationError,
    ForgetPassword,
    ResetPassword,
    VerifyOtp,
)
import sqlalchemy
import logging
import datetime


logger = logging.getLogger(__name__)

auth = Blueprint("auth", __name__, url_prefix="/api/")


@auth.route("/auth/signup", methods=["POST"])
def signup():
    schema = RegisterSchema()
    try:
        # it is already in the dict form then we use load not loads
        data = schema.load(request.get_json())
        logger.info("POST /api/auth/signup request initiated...")
    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    user_name = data["username"]
    email = data["email"]

    if User.query.filter_by(username=user_name).first():
        logger.warning(f"Signup attempt using existing email {email}")
        return user_already_exists("username already exist")

    if User.query.filter_by(email=email).first():
        logger.warning(f"Signup attempt using existing email {email}")
        return user_already_exists("email already in use")

    try:
        hashed_password = bcrypt.generate_password_hash(data["password"]).decode(
            "utf-8"
        )
        new_user = User(username=user_name, email=email,
                        password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        logger.info(f"User Created:  username={
                    user_name} user_id={new_user.id}")
        return jsonify({"message": f"{user_name} user created Sucessfully"}), 201

    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(
            f"Error in creating user: username={
                user_name}email={email} error={e}"
        )
        return internal_server_error()


# this is the most important part because we are generatingt the token , which is necessary for the stateless feature


@auth.route("/auth/login", methods=["POST"])
def login():
    schema = LoginSchema()
    try:
        data = schema.load(request.get_json())
        logger.info("POST /api/auth/login requested ...")
    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    if data.get("email"):
        # /one()  we can use that since there will only user with that username
        user = User.query.filter_by(email=data["email"]).first()
        if not user:
            logger.warning("There is Error, unable to query")
        logger.info(f"User used email={data['email']} as the login")
    else:
        user = User.query.filter_by(username=data["username"]).first()
        logger.info(f"User used username={data['username']}")

    if not user or not bcrypt.check_password_hash(user.password_hash, data["password"]):
        logger.warning(
            f"Failed login attempt: for identifier={
                data['email'] or data['username']
            } from IP={
                request.remote_addr
            } "  # will work if you dont deploy it on the server with reverse proxy nginx,
        )
        return unauthorized_error(msg="Invalid Credentials")

    try:
        token = generate_token(user.id)
        # here we have to give the jwt token for future
        if token:
            logger.info("Token is generated")
            return jsonify({"token": token})

    except Exception as e:
        logger.error(f"Token generation error:{e}")
        return internal_server_error(msg="Token Error generation..")


@auth.route("/auth/forget-password", methods=["POST"])
def forget_password():
    # it is bit like  we send the mail to the user no since we are the backend service he/she will authenticate user with otp
    # then if the otp written is valid then go and reser password
    schema = ForgetPassword()
    try:
        data = schema.load(request.get_json())
        logger.info("POST /api/auth/forget-password requested ...")
    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    user = User.query.filter_by(email=data["email"]).first()
    if user:
        otp = otp_generator()
        try:
            token = generate_token_otp(data["email"], user.id, otp)
            if token:
                logger.info("Forget-Password Token is generated")
                current_app.mail_service.send_mail(user, otp)
                logger.info(f"Email is sent: addr = {data['email']}...")

                # for testing purpose add the "otp":otp in it would be easier , only added otp
                return jsonify({"otp-token": token})
        except Exception as e:
            logger.error(f"Token generation error:{e}")
            return internal_server_error()
    else:
        logger.error(f"User not found with  : email = {data['email']}")
        return not_found(msg="User not found")


@auth.route("/auth/verify-otp", methods=["POST"])
@otp_token_chk
def verify_otp(token_otp, token_email):
    schema = VerifyOtp()
    try:
        data = schema.load(request.get_json())
        logger.info("POST /api/auth/verify-otp requested ...")
    except ValidationError as err:
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    if data["email"] != token_email:
        logger.warning(
            f"Authentication failed: token mail = {
                token_email
            } doesnt match to client mail ={data['email']} "
        )
        return forbidden_access("Forbidden,Not authorized to access other Data")

    if data["otp"] == token_otp:
        logger.info(f"OTP Verified: for user with {token_email} ")
        try:
            user = User.query.filter_by(email=data["email"]).first()
            if user:
                reset_token = generate_password_token(user.id, data["email"])
                if reset_token:
                    logger.info("Reset Token generated")

            else:
                logger.error(f"User not found with  : email = {data['email']}")
                not_found(msg="User not found")

        except Exception as e:
            logger.error(f"Token generation error:{e}")
            return internal_server_error()

        forget_pass = PasswordReset(
            reset_token=reset_token,
            expired_at=datetime.datetime.now(datetime.UTC)
            + datetime.timedelta(minutes=10),
            user_id=user.id,
        )
        db.session.add(forget_pass)
        db.session.commit()
        return jsonify({"reset-token": reset_token})

    else:
        logger.warning("OTP is invalid")
        return unauthorized_error(
            "Invalid OTP", reason="The provided OTP does not match"
        )


@auth.route("/auth/reset-password", methods=["POST"])
@reset_token_chk
def reset_password(user_id, email):
    schema = ResetPassword()
    user = User.query.filter_by(id=user_id, email=email).first()

    if not user:
        logger.error(
            f"User not found: user_id={user_id}, email={
                email}, ip={request.remot_addr}"
        )
        not_found(msg="User not found ")

    password_reset = (
        PasswordReset.query.filter_by(user_id=user.id)
        .order_by(PasswordReset.created_at.desc())
        .first()
    )

    try:
        data = schema.load(request.get_json())
        logger.info("POST api/auth/reset-password requested ...")
    except ValidationError as err:
        if password_reset:
            password_reset.attempts += 1
            db.session.commit()
        logger.error(f"Input error {err.messages}")
        return handle_marshmallow_error(err)

    # in future we can also think to implement ip ban for particular time period
    try:
        if bcrypt.check_password_hash(user.password_hash, data["new_password"]):
            if password_reset:
                password_reset.attempts += 1
                db.session.commit()

            return bad_request(
                error_type="PasswordReuseNotAllowed",
                msg="New password must be different from the old one",
            )
        new_password = bcrypt.generate_password_hash(
            data["new_password"]).decode()

        user.password_hash = new_password
        if password_reset:
            password_reset.used = True
        db.session.commit()
        logger.info(f"Password reset Sucessfull for user_id = {user_id}")
        return jsonify({"message": "Password created Sucessfully"}), 200

    except sqlalchemy.exc.SQLAlchemyError as e:
        logger.error(f"Error ocurred in updating password: {e}")
        return internal_server_error()

    except Exception as e:
        logger.error(f"Error ocurred in updating password: {e}")
        return internal_server_error()
