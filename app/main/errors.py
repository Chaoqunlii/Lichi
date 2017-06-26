from flask import render_template
from . import main


# 这里只导入main，不执行main下面的 所以避免了main\__init__.py
# 后面import errors的循环依赖

@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500
