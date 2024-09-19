from flask import render_template, jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt
from db import db
from models import ProjectModel, LikeModel
from sources.user import AuthorModel


blp = Blueprint(
    'projects',
    __name__,
    description='Operations with projects'
)


@blp.route('/')
class Home(MethodView):
    def get(self):
        posts = ProjectModel.query.all()
        return render_template(
            "home.html",
            posts=posts
        )


def get_username():
    token = get_jwt()
    if not token:
        return None
    username = token['sub']
    return username


@blp.route('/post/<int:post_id>/like')
class LikeProject(MethodView):
    @jwt_required()
    def post(self, post_id):
        try:
            post_model = ProjectModel.query.filter(ProjectModel.id == post_id).first()
            like = LikeModel.query.filter(LikeModel.post_id == post_id, LikeModel.author_id).first()
            username = get_username()
            author = AuthorModel.query.filter(AuthorModel.username == username).first()
            if like:
                post_model.likes_count -= 1
                return jsonify({"message": "success dislike"}), 200

            new_like = LikeModel(post_id=post_id, author_id=author.id)
            post_model.likes_count += 1
            db.session.add(new_like)
            db.session.commit()
            return jsonify({"message": "success like"}), 200

        except Exception as e:
            print(e)
