from db import db
from flask_jwt_extended import jwt_required, create_access_token
from flask_jwt_extended import get_jwt, set_access_cookies, unset_access_cookies
import hashlib
from flask import render_template, render_template_string
from flask.views import MethodView
from models.user import AuthorModel
from models.jwt import BlocklistJwt
from flask_smorest import Blueprint, abort
from schemas import AuthorLoginSchema
from flask import jsonify
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
import uuid
import random
import qrcode


blp = Blueprint('qr_code', __name__, 'operations with QR code')


@blp.route('/qr/login')
class QrLogin(MethodView):
    def get(self, token: str = None, mfa_code: str = None):

        if token is None or mfa_code is None:
            return render_template('error.html', text_error='missing arguments')

        if not AuthorModel.query.filter(token == token):
            abort('invalid token')

        author = AuthorModel.query(token=token).first()
        if not author.token == token and not author.mfa_code == mfa_code:
            return render_template('error.html', text_error='invalid token or mfa_code, please regen your qr code')


@blp.route('/qr/generate')
class QRGenerator(MethodView):
    @jwt_required()
    @blp.get('/')
    def gen_qr(self):
        jwt_token = get_jwt()
        token = uuid.uuid4().hex
        mfa_code = random.randint(1111, 9999)
        author = AuthorModel.query.filter(username=jwt_token['username']).first()
        author.mfa_code = mfa_code
        author.token = token
        db.session.add(author)
        db.session.commit()
        qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4,)
        qr.add_data(f'http://domen.com/qr/login?token={token}&mfa_code={mfa_code}')
        qr.make(fit=True)
        img = qr.make_image(fill_color="blue", back_color='white')
        img.save('qr.png')
        qr_in_str = qr.print_ascii()



