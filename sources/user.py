from datetime import datetime
import hashlib
import threading
from flask import jsonify, render_template, render_template_string
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt, set_access_cookies, unset_access_cookies
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import AuthorLoginSchema
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import AuthorModel
from models import BlocklistJwt
from models import ProjectModel
from sources.qr import QRGenerator
import uuid
import random
import os

BASE_DIR = r"C:\Users\ilya1\PycharmProjects\standoff_app"


blp = Blueprint(
    "users",
    __name__,
    description='Operations with users'
)


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):
        if AuthorModel.query.filter(user_data["username"] == AuthorModel.username).first():
            abort(409, message="User already exists")
        user = AuthorModel(username=user_data["username"],
                           password=hashlib.sha256(user_data["password"].encode()).hexdigest())
        db.session.add(user)
        db.session.commit()
        return {"Message": "success"}, 201

    def get(self):
        return render_template('register.html')


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):
        author = AuthorModel.query.filter(AuthorModel.username == user_data["username"]).first()
        if not author or hashlib.sha256(user_data["password"].encode()).hexdigest() != author.password:
            abort(400, message="Username or password is invalid")

        if user_data["username"] == 'admin':
            access_token = create_access_token(identity=user_data["username"],
                                               additional_claims={"is_administrator": True}, fresh=True)
        else:
            access_token = create_access_token(identity=author.username, fresh=True)

        resp = jsonify({"message": "success login"})
        set_access_cookies(resp, access_token)
        return resp, 200

    def get(self):
        return render_template('login.html')


@blp.route('/profile')
class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        token = get_jwt()
        author = AuthorModel.query.filter(AuthorModel.username == token['sub']).first()
        posts = ProjectModel.query.filter(ProjectModel.author_id == author.id)
        return render_template('profile.html', user=token['sub'], posts=posts)


@blp.route('/profile/qr-login')
class UserProfileQr(MethodView):
    @jwt_required()
    def get(self):
        jwt_token = get_jwt()
        token = uuid.uuid4().hex
        mfa_code = random.randint(1111, 9999)
        filename = uuid.uuid4().hex + '.png'
        author = AuthorModel.query.filter(AuthorModel.username == jwt_token['sub']).first()
        author.mfa_code = mfa_code
        author.token = token
        db.session.add(author)
        db.session.commit()
        file_path = os.path.join(BASE_DIR, filename)
        qr_handler = QRGenerator(token, mfa_code, file_path)
        qr_handler.gen_qr()
        threading.Thread(target=qr_handler.rm_qr).start()
        return {"Message": "success"}, 200


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def get(self):
        resp = jsonify({"message": "logout successful"})
        try:
            unset_access_cookies(resp)
            jti = get_jwt()["jti"]
            now = datetime.now()
            db.session.add(BlocklistJwt(jti=jti, created_at=now))
            db.session.commit()
            return resp
        except SQLAlchemyError as e:
            print(f"error: {e}")
            return resp
