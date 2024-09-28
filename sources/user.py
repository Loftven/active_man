from datetime import datetime
import hashlib
import threading
import os
import uuid

from flask import jsonify, render_template, redirect, url_for
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import (
    get_jwt,
    set_access_cookies,
    unset_access_cookies
)
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from constants import BASE_DIR
from db import db
from forms import ApproveForm
from models import AuthorModel
from models import BlocklistJwt
from schemas import AuthorLoginSchema
from sources.qr import QRGenerator


blp = Blueprint(
    'users',
    __name__,
    description='Operations with users'
)


@blp.route('/register')
class UserRegister(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):
        if AuthorModel.query.filter(
                user_data['username'] == AuthorModel.username
        ).first():
            abort(409, message='User already exists')
        user = AuthorModel(
            username=user_data['username'],
            password=hashlib.sha256(user_data['password'].encode()
                                    ).hexdigest()
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('users.UserLogin'))

    def get(self):
        return render_template('register.html')


@blp.route('/login')
class UserLogin(MethodView):
    @blp.arguments(AuthorLoginSchema)
    def post(self, user_data):
        author = AuthorModel.query.filter(
            AuthorModel.username == user_data['username']
        ).first()
        if not author or hashlib.sha256(
                user_data['password'].encode()
        ).hexdigest() != author.password:
            abort(400,
                  message='Username or password is invalid'
                  )

        access_token = create_access_token(
            identity=author.username,
            fresh=True
        )

        resp = jsonify({'message': 'success login'})
        set_access_cookies(resp, access_token)
        return resp, 200

    def get(self):
        return render_template('login.html')


@blp.route('/profile')
class UserProfile(MethodView):
    @jwt_required()
    def get(self):
        try:
            token = get_jwt()
            author = AuthorModel.query.filter(
                AuthorModel.username == token['sub']
            ).first()
            if token['sub'] == 'admin':
                return redirect(url_for('admin.home'))
            if not author.privileges:
                return render_template(
                    'profile.html',
                    user=token['sub'],
                    args=None
                )

            return render_template(
                'profile.html',
                user=token['sub'],
                args=(author.first_name,
                      author.last_name,
                      author.cityzen_id,
                      author.privileges
                      )
            )
        except SQLAlchemyError as e:
            print(e)


@blp.route('/profile/approve')
class UserProfileApprove(MethodView):
    @jwt_required()
    def get(self):
        token = get_jwt()
        form = ApproveForm()
        return render_template(
            'approve.html',
            form=form,
            user=token['sub']
        )

    @jwt_required()
    def post(self):
        form = ApproveForm()
        if form.validate_on_submit():
            token = get_jwt()
            user = AuthorModel.query.filter(
                AuthorModel.username == token['sub']
            ).first()

            if (len(form.first_name.data) > 8 or
                    len(form.last_name.data) > 8 or
                    len(form.cityzen_id.data) > 20
            ):
                return render_template(
                    'error.html',
                    text_error='Вас нет в базе данных города,'
                               ' обратитесь в администрацию'
                )

            if user.privileges == 1:
                return render_template(
                    'error.html',
                    text_error='Аккаунт уже подтвержден.'
                               ' Участвуйте в голосованиях и '
                               'участвуйте в развитии города!'
                )

            query = text('select id from author where '
                         'first_name=\'{first_name}\' and'
                         ' last_name=\'{last_name}\' and '
                         'cityzen_id=\'{cityzen_id}\''.format(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                cityzen_id=form.cityzen_id.data
            ))

            result = db.session.execute(query)
            exists = result.fetchall()

            if not exists:
                return render_template(
                    'error.html',
                    text_error='Вас нет в базе данных города,'
                               ' обратитесь в администрацию'
                )

            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.cityzen_id = form.cityzen_id.data
            user.privileges = 1
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('users.UserProfile'))
        return render_template(
            'approve.html',
            form=form
        )


@blp.route('/profile/qr-login')
class UserProfileQr(MethodView):
    @jwt_required()
    def get(self):
        jwt_token = get_jwt()
        token = uuid.uuid4().hex
        filename = uuid.uuid4().hex + '.png'
        author = AuthorModel.query.filter(
            AuthorModel.username == jwt_token['sub']
        ).first()

        if author.privileges != 1:
            return {'error': 'Подтвердите свою учетную запись,'
                             ' необходимо ввести ФИ и id гражданина'
                    }

        author.token = token
        db.session.add(author)
        db.session.commit()
        file_path = os.path.join(BASE_DIR, filename)
        qr_handler = QRGenerator(token, author.id, file_path)
        qr_handler.gen_qr()
        threading.Thread(target=qr_handler.rm_qr).start()
        return render_template('qr.html', path=url_for('static', filename=filename))


@blp.route('/logout')
class UserLogout(MethodView):
    @jwt_required()
    def get(self):
        resp = jsonify({'message': 'logout successful'})
        try:
            unset_access_cookies(resp)
            jti = get_jwt()['jti']
            now = datetime.now()
            db.session.add(BlocklistJwt(jti=jti, created_at=now))
            db.session.commit()
            return redirect(url_for('projects.home'))
        except SQLAlchemyError as e:
            print(f'error: {e}')
            return resp
