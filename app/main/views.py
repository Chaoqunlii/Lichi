from flask import render_template, session, redirect, url_for, flash, current_app, abort
from datetime import datetime
from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm
from .. import db
from ..models import User, Role, Post, PostContent
from ..email import send_email
from flask_login import login_required, current_user
from ..decorators import admin_required


@main.route('/', methods=['GET', 'POST'])
def index():

    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        post = Post(author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        postContent = PostContent(version_intro=form.version_intro.data,
                                  body=form.body.data,
                                  post_id=post.id)

        db.session.add(postContent)
    elif not current_user.can(Permission.WRITE_ARTICLES) and\
            form.validate_on_submit():
        flash('使用发布功能需要先登录')

    postContents = PostContent.query.order_by(PostContent.timestamp.desc()).all()
    return render_template('index.html', form=form, postContents=postContents)



@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    postContents = PostContent.order_by(PostContent.timestamp.desc())
    return render_template('user.html', user=user)


@main.route('/eidt-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('您的用户资料已更新')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('用户信息已更新')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location = user.location
    form.about_me = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed'


from ..decorators import admin_required, permission_required
from ..models import Permission


@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return '管理员大人~~'


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return '协管员大人'
