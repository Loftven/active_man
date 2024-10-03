import os
import uuid

from flask import (
    current_app,
    render_template,
    redirect,
    request,
    send_file,
    url_for
)
from flask_jwt_extended import get_jwt_identity
from flask.views import MethodView
from flask_smorest import Blueprint
from sqlalchemy.exc import SQLAlchemyError
from PIL import Image
from werkzeug.utils import secure_filename

from db import db
from decorator import admin_required
from forms import PostForm
from latex import generate_latex
from models import AuthorModel
from models import ProjectModel
from schemas import ProjectClose


blp = Blueprint('admin',
                __name__,
                description='Admin panel'
                )


def is_allowed_filename(filename):
    return ('.' in filename and filename.rsplit('.', 1)[1].lower()
            in current_app.config['UPLOAD_EXTENSIONS'])


@blp.route('/admin', endpoint='home')
class AdminHome(MethodView):
    @admin_required
    def get(self):
        author = AuthorModel.query.filter(AuthorModel.username == get_jwt_identity()).first()
        return render_template(
            'admin_profile.html',
            user='admin',
            args=(
                author.first_name,
                author.last_name,
                author.cityzen_id,
                author.privileges
            )
        )


@blp.route('/admin/post')
class CreatePost(MethodView):
    @admin_required
    def post(self):
        form = PostForm()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
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
                            image.save(os.path.join(
                                current_app.config['UPLOAD_FOLDER'],
                                filename
                            ))
                            filenames.append(filename)
                        except (IOError, SyntaxError) as e:
                            return render_template(
                                'error.html',
                                text_error=e
                            )

            project_model = ProjectModel(
                title=title,
                content=content,
                image_names=filenames
            )
            db.session.add(project_model)
            db.session.commit()
            return redirect(url_for('projects.list_posts'))
        return render_template(
            'posts.html',
            form=form
        )

    @admin_required
    def get(self):
        form = PostForm()
        return render_template(
            'create_post.html',
            form=form
        )


@blp.route('/admin/post/change/<int:post_id>')
class UpdatePost(MethodView):
    @admin_required
    def post(self, post_id):
        try:
            project = ProjectModel.query.get_or_404(post_id)
            form = PostForm(obj=project)
            if form.validate_on_submit():
                project.title = form.title.data
                project.content = form.content.data
                images = request.files.getlist('images')
                filenames = []
                if images:
                    for image in images:
                        if image and is_allowed_filename(image.filename):
                            try:
                                img = Image.open(image)
                                img.verify()
                                filename = (image.filename)
                                image.seek(0)
                                image.save(os.path.join(
                                    current_app.config['UPLOAD_FOLDER'],
                                    filename
                                ))
                                filenames.append(filename)
                            except (IOError, SyntaxError) as e:
                                return render_template(
                                    'error.html',
                                    text_error=e
                                )
                if project.image_names:
                    for image in project.image_names:
                        try:
                            os.remove(
                                os.path.join(current_app.config['UPLOAD_FOLDER'],
                                             image
                                             )
                            )
                        except OSError as e:
                            print(e)
                project.image_names = filenames
                db.session.add(project)
                db.session.commit()
            return redirect(url_for('projects.list_posts'))

        except SQLAlchemyError as e:
            return render_template(
                'error.html',
                text_error=e
            )


    @admin_required
    def get(self, post_id):
        project = ProjectModel.query.get_or_404(post_id)
        form = PostForm(
            title=project.title,
            content=project.content
        )
        return render_template(
            'edit_post.html',
            post=project,
            form=form
        )


@blp.route('/admin/post/<int:post_id>', endpoint='post_delete')
class DeletePost(MethodView):
    @admin_required
    def delete(self, post_id):
        try:
            post_model = ProjectModel.query.get_or_404(post_id)
            db.session.delete(post_model)
            db.session.commit()
            return {'Message:': 'success'}, 201
        except SQLAlchemyError as e:
            return render_template(
                'error.html',
                text_error=e
            )


@blp.route('/admin/post/close/<int:post_id>')
class ProjectClose(MethodView):
    @admin_required
    def get(self, post_id):
        try:
            post = ProjectModel.query.filter(
                ProjectModel.id == post_id
            ).first()

            if post.likes_count < current_app.config['LIKES_REQUIRED']:
                return render_template(
                    'error.html',
                    text_error='Извини, нельзя согласовать'
                               ' проект без одобрения большинства'
                               ' граждан. Удали проект, если он '
                               'никому не понравился...'
                )

            latex_code = generate_latex(
                post.title,
                post.content,
                post.image_names
            )
            filename = uuid.uuid4().hex + '.tex'
            filepath = os.path.join(
                current_app.config['LATEX_FOLDER'],
                filename
            )

            with open(filepath, 'w') as f:
                f.write(latex_code)
            os.system(f'pdflatex -shell-escape -output-directory={current_app.config["LATEX_FOLDER"]} {filepath}')

            return send_file(filepath.rsplit('.', 1)[0] + '.pdf', as_attachment=True)

        except Exception as e:
           return render_template(
               'error.html',
               text_error=e
           )

    @admin_required
    @blp.arguments(ProjectClose)
    def post(self, helper, project_id):
        try:
            #TODO: добавить в образ виртуалки LaTeX м проверить работу эксплойта
            post = ProjectModel.query.filter(
                ProjectModel.id == project_id
            ).first()

            if helper is None:
                return render_template(
                    'error.html',
                    text_error='Неверное имя параметра'
                )
            if not helper['helper']:
                return render_template(
                    'error.html',
                    text_eror='Указано неверное значение параметра'
                )

            latex_code = generate_latex(
                post.title,
                post.content,
                post.image_names
            )
            filename = uuid.uuid4().hex + '.tex'
            filepath = os.path.join(
                current_app.config['LATEX_FOLDER'],
                filename
            )

            with open(filepath, 'w') as f:
                f.write(latex_code)
            os.system(f'pdflatex -shell-escape -output-directory={current_app.config["LATEX_FOLDER"]} {filepath}')

            return send_file(filepath.rsplit('.', 1)[0] + '.pdf', as_attachment=True)

        except Exception as e:
           return render_template(
               'error.html',
               text_error=e
           )