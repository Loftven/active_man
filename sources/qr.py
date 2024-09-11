from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask import render_template, render_template_string
from flask.views import MethodView
from models import AuthorModel
from flask_smorest import Blueprint, abort
from flask import jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import uuid
import qrcode
import asyncio
import os
import time


blp = Blueprint('qr_code', __name__, 'operations with QR code')


@blp.route('/login/qr')
class QrLogin(MethodView):
    def get(self, token: str = None, mfa_code: str = None):

        if token is None or mfa_code is None:
            return render_template('error.html', text_error='missing arguments')

        try:
            author = AuthorModel.query.filter(mfa_code == mfa_code).first()
            if not author.token == token and not author.mfa_code == mfa_code:
                return render_template('error.html', text_error='invalid token or mfa_code, please regen your qr code')

        except SQLAlchemyError as e:
            abort(404, message='invalid token or mfa code')


class QRGenerator(MethodView):

    def __init__(self, token, mfa_code, file_path):
        self.token = token
        self.mfa_code = mfa_code
        self.file_path = file_path

    def gen_qr(self):
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
        qr.add_data(f'http://domen.com/qr/login?token={self.token}&mfa_code={self.mfa_code}')
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color='white')
        img.save(self.file_path)

    def rm_qr(self):
        time.sleep(300)  # Ждем 5 минут
        try:
            os.remove(self.file_path)
        except OSError as e:
            print(e)




