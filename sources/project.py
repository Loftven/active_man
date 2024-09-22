from flask import render_template, jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity,
    verify_jwt_in_request
)
from schemas import PostSchema
from sqlalchemy.exc import SQLAlchemyError

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
        return render_template(
            'home.html',
        )


@blp.route('/posts', endpoint='list_posts')
class ListPosts(MethodView):
    def get(self):
        posts = ProjectModel.query.all()
        return render_template(
            'posts/posts.html',
            posts=posts
        )


@blp.route('/posts', endpoint='post_create')
class CreatePost(MethodView):
    @jwt_required()
    @blp.arguments(PostSchema)
    @blp.response(200, PostSchema)
    def post(self, post_data):
        try:
            token = get_jwt()
            user = AuthorModel.query.filter(
                AuthorModel.username == token['sub']
            ).first()
            post_model = ProjectModel(
                author_id=user.id,
                **post_data
            ) # you need create another object!!
            db.session.add(post_model)
            db.session.commit()
            return {"success": "message"}, 201
        except SQLAlchemyError as e:
            print(e)

    def get(self):
        return render_template('posts/post_form.html')


@blp.route('/posts/<int:post_id>', endpoint='get_post')
class GetPost(MethodView):
    def get(self, post_id):
        post = ProjectModel.query.get_or_404(post_id)
        return render_template(
            'posts/post_detail.html',
            post=post)


@blp.route('/posts/<int:post_id>', endpoint='post_update')
class UpdatePost(MethodView):
    @jwt_required()
    @blp.arguments(PostSchema)
    def patch(self, user_data, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token['sub'] != post_model.author.username:
                return jsonify(
                    {'Message': 'It isn\'t your post',
                     'Error': 'Access is denied'}
                ), 401

            post_model.title = user_data['title']
            post_model.content = user_data['content']
            db.session.add(post_model)
            db.session.commit()
            return {'Message:': 'success'}, 201
        except SQLAlchemyError as e:
            return {'error: {}'.format(e): 'message'}, 400

    @jwt_required()
    def get(self, post_id):
        post = ProjectModel.query.get_or_404(post_id)
        return render_template(
            'posts/post_form.html',
            post=post)


@blp.route('/posts/<int:post_id>', endpoint='post_delete')
class DeletePost(MethodView):
    @jwt_required()
    def delete(self, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            jwt_token = get_jwt()
            if jwt_token['sub'] != post_model.author.username:
                return jsonify(
                    {'Message': 'It isn\'t your post',
                     'Error': 'Access is denied'}
                ), 401
            db.session.delete(post_model)
            db.session.commit()
            return {'Message': 'Post deleted successfully'}, 201
        except SQLAlchemyError as e:
            return {'error: {}'.format(e): 'message'}, 400


@blp.route('/posts/<int:post_id>/like', endpoint='like_post')
class LikePost(MethodView):
    @jwt_required()
    def post(self, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            current_user_id = get_jwt_identity()
            like = LikeModel.query.filter_by(
                post_id=post_id,
                author_id=current_user_id
            ).first_or_none()
            if like:
                post_model.likes_count -= 1
                return jsonify({'message': 'success dislike'}), 200

            new_like = LikeModel(
                post_id=post_id,
                author_id=current_user_id
            )
            post_model.likes_count += 1
            db.session.add(new_like)
            db.session.commit()
            return jsonify({'message': 'success like'}), 200

        except Exception as e:
            print(e)
            return jsonify({"message": "Error occurred"}), 500
