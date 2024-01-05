"""
This module takes care of starting the API Server, Loading the DB, and Adding the endpoints
"""
from datetime import timedelta
from flask import Flask, request, jsonify, url_for, Blueprint
from api.models import db, User, TokenBlockedList
from api.utils import generate_sitemap, APIException
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, get_jti

api = Blueprint('api', __name__)
app = Flask(__name__)
bcrypt = Bcrypt(app)


@api.route('/hello', methods=['POST', 'GET'])
def handle_hello():

    response_body = {
        "message": "Hello! I'm a message that came from the backend, check the network tab on the google inspector and you will see the GET request"
    }

    return jsonify(response_body), 200


@api.route("/signup", methods=["POST"])
def user_create():
    data = request.get_json()
    print(data)
    new_user = User.query.filter_by(email=data["email"]).first()
    if (new_user is not None):
        return jsonify(
            {
                "msg": "Email already registered"
            }
        ), 400
    secure_password = bcrypt.generate_password_hash(
        data["password"], rounds=None).decode("utf-8")
    print(new_user is None)
    new_user = User(email=data["email"],
                    password=secure_password, is_active=True)
    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.serialize()), 201


@api.route("/login", methods=["POST"])
def user_login():
    user_email = request.json.get("email")
    user_password = request.json.get("password")
    # Search user by email
    user = User.query.filter_by(email=user_email).first()
    if user is None:
        return jsonify({"Message": "User not found"}), 401

    # Verify the password
    if not bcrypt.check_password_hash(user.password, user_password):
        return jsonify({"message": "Wrong password"}), 401
    # Generate the token
    access_token = create_access_token(identity=user.id)
    access_jti = get_jti(access_token)
    refresh_token = create_refresh_token(identity=user.id, additional_claims={
                                         "accessToken": access_jti})
    # Return the token
    return jsonify({"accessToken": access_token, "refreshToken": refresh_token})

@api.route("/changepassword", methods=["POST"])
@jwt_required()
def change_password():
    new_password=request.json.get("password")
    user_id=get_jwt_identity()
    secure_password = bcrypt.generate_password_hash(new_password, rounds=None).decode("utf-8")
    user=User.query.get(user_id)
    user.password=secure_password
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg":"Password updated"})

@api.route("/recoverypassword", methods=["POST"])
def recovery_password():
    user_email=request.json.get("email")
    user=User.query.filter_by(email=user_email).first()
    if user is None:
        return jsonify({"Message": "User not found"}), 401
    # Generate temporary token for password change
    access_token = create_access_token(identity=user.id, additional_claims={"type":"password"})
    return jsonify({"recoveryToken":access_token})
    # Send link with token via email for password change


@api.route("/helloprotected", methods=["GET"])
@jwt_required()
def hello_protected_get():
    user_id = get_jwt_identity()
    return jsonify({"userId": user_id, "message": "Hello protected route"})


@api.route("/logout", methods=["POST"])
@jwt_required()
def user_logout():
    jwt = get_jwt()["jti"]
    tokenBlocked = TokenBlockedList(jti=jwt)
    db.session.add(tokenBlocked)
    db.session.commit()
    return jsonify({"msg": "Token revoked"})


@api.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def user_refresh():
    # Identifiers for old tokens
    jti_refresh = get_jwt()["jti"]
    jti_access=get_jwt()["accessToken"]
    # Block old tok

