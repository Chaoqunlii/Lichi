from flask import render_template, redirect, url_for, flash, current_app, abort, request, make_response
from datetime import datetime
from . import main
from .forms import PostForm, EditProfileForm, EditProfileAdminForm, CommentForm
from .. import db
from ..models import User, Role, Post, PostContent, Permission, Comment
from flask_login import login_required, current_user
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries

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
    elif not current_user.can(Permission.WRITE_ARTICLES) and \
            form.validate_on_submit():
        flash('使用发布功能需要先登录')

    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    page = request.args.get('page', 1, type=int)
    pagination = query.order_by(Post.last_updated_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('index.html', form=form, posts=posts,
                           pagination=pagination, current_time=datetime.utcnow(),
                           show_followed=show_followed)

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect((url_for('.index'))))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()

    # postContents = PostContent.query.order_by(PostContent.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.last_updated_time.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


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


@main.route('/post/<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    postContent = post.postContents.all()[-1]
    return redirect(url_for('.postContent', id=postContent.id))
    # return render_template('postContent.html', postContent=postContent)

@main.route('/postContent/<int:id>', methods=['GET', 'POST'])
def postContent(id):
    postContent = PostContent.query.get_or_404(id)
    form = CommentForm()
    if not current_user.is_authenticated:
        flash('评论需先登录')
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          postContent=postContent,
                          author=current_user._get_current_object())
        db.session.add(comment)
        flash('评论成功')
        return redirect(url_for('.postContent', id=postContent.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (postContent.comments.count() - 1)/\
            current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = postContent.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('postContent.html', postContent=postContent, form=form,
                           comments=comments, pagination=pagination)

@main.route('/edit/<int:id>', methods=["GET", "POST"])
def edit(id):
    post = Post.query.get_or_404(id)
    # postContent = post.postContents[len(post.postContents.all()) - 1]
    postContent = post.postContents.all()[-1]
    if current_user != post.author and \
            not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        postContent = PostContent(version_intro=form.version_intro.data,
                                  body=form.body.data,
                                  post_id=post.id)
        db.session.add(postContent)
        flash('您更新了内容版本')
        return redirect(url_for('.post', id=post.id))
    form.body.data = postContent.body
    form.version_intro.data = postContent.version_intro
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效的用户')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注过ta了')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('你现在成功关注了 %s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效的用户')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你没有关注该用户')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('你不再关注 %s' % username)
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效的用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='ta关注的人', endpoint='.followers',
                           pagination=pagination, follows=follows)

@main.route('/followed-by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效的用户')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title='关注ta的人',
                           endpoint='.followed_by', pagination=pagination, follows=follows)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False
    )
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))

@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %f\nContext: %s\n'\
                %(query.statement, query.parameters, query.duration, query.context))
    return response



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
