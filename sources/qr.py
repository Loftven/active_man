import os
import time

from flask import render_template, request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from flask_jwt_extended import create_access_token, set_access_cookies
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import qrcode

from constants import TIME_QR
from models import AuthorModel

blp = Blueprint('qr_code', __name__, 'operations with QR code')


@blp.route('/login/qr')
class QrLogin(MethodView):
    def get(self):
        token = request.args.get('token')
        id = request.args.get('id')

        if token is None or id is None:
            return render_template(
                'error.html',
                text_error='missing arguments'
            )

        try:
            author = AuthorModel.query.filter(
                AuthorModel.id == id
            ).first()
            if not AuthorModel.query.filter(
                    AuthorModel.token == token
            ).first():
                return render_template(
                    'error.html',
                    text_error='invalid or expired token,'
                               ' please regen your qr code'
                )

            access_token = create_access_token(
                identity=author.username,
                fresh=True
            )
            resp = jsonify({'message': 'success login'})
            set_access_cookies(resp, access_token)

            return resp, 200

        except SQLAlchemyError as e:
            abort(404, message='invalid token')


class QRGenerator(MethodView):

    def __init__(self, token, id, file_path):
        self.token = token
        self.id = id
        self.file_path = file_path

    def gen_qr(self):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(
            f'http://domen.com/qr/login?token={self.token}&id={self.id}'
        )
        qr.make(fit=True)
        img = qr.make_image(fill_color='blue', back_color='white')
        img.save(self.file_path)

    def rm_qr(self):
        time.sleep(TIME_QR)
        try:
            os.remove(self.file_path)
            engine = create_engine('sqlite:///instance/data.db')
            Session = sessionmaker(bind=engine)
            session = Session()
            author = session.query(AuthorModel).filter(
                AuthorModel.id == self.id
            ).first()
            if author:
                author.token = None
                session.commit()
        except Exception as e:
            print(e)
            session.rollback()
        finally:
            session.close()
