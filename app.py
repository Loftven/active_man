from datetime import datetime, timedelta, timezone
from db import db
import hashlib
import os
from flask import Flask, jsonify
import asyncio
from sources.project import blp as project_blp
from sources.user import blp as author_blp
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    JWTManager,
    set_access_cookies
)

from models import AuthorModel, BlocklistJwt


def create_app(db_url=None):
    app = Flask(__name__, template_folder='templates')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv(
        "DATABASE_URL",
        "sqlite:///data.db"
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'enc_key_for_production_864792'
    app.config['JWT_COOKIE_SECURE'] = False # change to True in production
    app.config['JWT_TOKEN_LOCATION'] = ["cookies", "headers"]
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=5)
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False
    db.init_app(app)
    jwt = JWTManager(app)


    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(
                now + timedelta(minutes=30)
            )

            if target_timestamp > exp_timestamp:
                access_token = create_access_token(
                    identity=get_jwt_identity()
                )
                set_access_cookies(response, access_token)

            response.headers['Access-Control-Allow-Origin'] = '*'
            return response

        except (RuntimeError, KeyError) as e:
            print(f'Error: {e}')
            return response

    with app.app_context():
        db.create_all()
        admin = AuthorModel.query.filter(AuthorModel.username == 'admin').first()
        if admin is None:
            admin = {
                "username": "admin",
                "password": hashlib.sha256("r04S9[*.£Wb6".encode()).hexdigest(),
                "mfa_code": "5432",
                "token": "e74568eb3ea846b3b50dd121c9d8ae1b"
            }
            db.session.add(AuthorModel(**admin))
            db.session.commit()
            print('Создан пользователь админ')
            # добавить в конце создание проектов и накрутку лайков для проектов
        else:
            print("Админ уже был создан")

    app.register_blueprint(project_blp)
    app.register_blueprint(author_blp)

    @jwt.expired_token_loader
    def expired_token_loader(jwt_header, jwt_payload):
        return jsonify(
            {"Message": "The token as expired",
             "error": "token_expired"}
        ), 401

    @jwt.unauthorized_loader
    def unauthorized_loader_callback(error):
        return jsonify(
            {'Message': 'token is not found.',
             'error': 'missing_token'}
        ), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify(
            {'Message': 'Signature verification failed.',
             'error': 'invalid_token'}
        ), 401

    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload['jti']
        token = db.session.query(
            BlocklistJwt.id
        ).filter_by(jti=jti).scalar()
        return token is not None

    return app


appl = create_app()
appl.run(host='0.0.0.0', debug=True)