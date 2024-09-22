from flask import render_template, jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import jwt_required, get_jwt, get_jwt_identity
from db import db
from models import ProjectModel, LikeModel
from sources.user import AuthorModel


blp = Blueprint(
    'projects',
    __name__,
    description='Operations with projects'
)


@blp.route('/', endpoint='home')
class Home(MethodView):
    def get(self):
        posts = ProjectModel.query.all()
        return render_template(
            "home.html",
            posts=posts
        )


@blp.route('/posts', endpoint='list_posts')
class ListPosts(MethodView):
    def get(self):
        posts = ProjectModel.query.all()
        return render_template(
            "posts.html",
            posts=posts
        )


@blp.route('/post/<int:post_id>/like', endpoint='like_post')
class LikeProject(MethodView):
    @jwt_required()
    def get(self, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            current_user = AuthorModel.query.filter(AuthorModel.username == get_jwt_identity()).first()

            like = LikeModel.query.filter(
                LikeModel.project_id == post_id,
                LikeModel.author_id == current_user.id
            ).first()
            if like:
                post_model.likes_count -= 1
                db.session.delete(like)
                db.session.commit()
                return jsonify({'message': 'success dislike'}), 200

            new_like = LikeModel(
                project_id=post_id,
                author_id=current_user.id
            )
            post_model.likes_count += 1
            db.session.add(new_like)
            db.session.commit()
            return jsonify({'message': 'success like'}), 200

        except Exception as e:
            print(e)
