from flask import jsonify, render_template, redirect, url_for, current_app, request
from flask_jwt_extended import jwt_required
from flask_jwt_extended import get_jwt
from flask.views import MethodView
from flask_smorest import Blueprint
from forms import PostForm
from werkzeug.utils import secure_filename
from decorator import admin_required
from sqlalchemy.exc import SQLAlchemyError
from db import db
from schemas import PostSchema
from models import ProjectModel
from PIL import Image
import os

blp = Blueprint('admin',
                __name__,
                description='Admin panel'
                )


def is_allowed_filename(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in current_app.config['UPLOAD_EXTENSIONS']


@blp.route('/admin/post/change/<int:post_id>')
class ChangePost(MethodView):
    @jwt_required()
    def delete(self, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token["sub"] != post_model.author.username:
                return jsonify(
                    {"Message": "It isn't your post",
                     "Error": "Access is denied"}
                ), 401
            db.session.delete(post_model)
            db.session.commit()
            return {"Message:": "success"}, 201
        except SQLAlchemyError as e:
            return {"error: {}".format(e): "message"}, 400

    @jwt_required()
    @blp.arguments(PostSchema)
    def post(self, user_data, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token["sub"] != post_model.author.username:
                return jsonify(
                    {"Message": "It isn't your post",
                     "Error": "Access is denied"}
                ), 401

            post_model.title = user_data["title"]
            post_model.content = user_data["content"]
            db.session.add(post_model)
            db.session.commit()
            return {"Message:": "success"}, 201

        except SQLAlchemyError as e:
            return {"error: {}".format(e): "message"}, 400

    @jwt_required()
    def get(self, post_id):
        post = ProjectModel.query.get_or_404(post_id)
        return render_template(
            'change.html',
            post=post)


@blp.route('/admin/post')
class CreatePost(MethodView):
    @admin_required
    def post(self):
        form = PostForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            print(request.files)
            images = request.files.getlist('images')
            filenames = []
            if images:
                for image in images:
                    if image and is_allowed_filename(image.filename):
                        try:
                            img = Image.open(image)
                            img.verify()
                            filename = secure_filename(image.filename)
                            image.seek(0)
                            image.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                            filenames.append(filename)
                        except (IOError, SyntaxError) as e:
                            return render_template('error.html', text_error=e)

            project_model = ProjectModel(title=title, content=content, image_names=filenames)
            db.session.add(project_model)
            db.session.commit()
            return redirect(url_for('projects.Home'))
        return render_template('projects.html', form=form)

    @admin_required
    def get(self):
        form = PostForm()
        return render_template('create_post.html', form=form)
