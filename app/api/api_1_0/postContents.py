from flask import jsonify, request, g, abort, url_for, current_app
from ...import db
from ...models import PostContent, Permission, Post
from . import api
from .decorators import permission_required
from .errors import forbidden


@api.route('/postContents/')
def get_postContents():
    page = request.args.get('page', 1, type=int)
    pagination = PostContent.query.paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    postContents = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_postContents', page=page-1, _external=True)
    next = None
    if pagination.has_next:
        next = url_for('api.get_postContents', page=page+1, _external=True)
    return jsonify({
        'postContents': [postContent.to_json() for postContent in postContents],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/postContents/<int:id>')
def get_postContent(id):
    postContent = PostContent.query.get_or_404(id)
    return jsonify(postContent.to_json())


@api.route('/postContents/', methods=['POST'])
@permission_required(Permission.WRITE_ARTICLES)
def new_postContent():
    postContent = PostContent.from_json(request.json)
    post = Post()
    post.author = g.current_user
    db.session.add(post)
    db.session.commit()
    db.session.add(postContent)
    db.session.commit()
    return jsonify(post.to_json()), 201, \
        {'Location': url_for('api.get_post', id=post.id, _external=True)}


@api.route('/posts/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE_ARTICLES)
def edit_post(id):
    post = Post.query.get_or_404(id)
    if g.current_user != post.author and \
            not g.current_user.can(Permission.ADMINISTER):
        return forbidden('Insufficient permissions')
    post.body = request.json.get('body', post.body)
    db.session.add(post)
    return jsonify(post.to_json())
