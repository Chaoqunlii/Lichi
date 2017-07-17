from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Regexp, Length, Email
from wtforms import ValidationError
from ..models import User, Role


class NameForm(FlaskForm):
    name = StringField('你的名字?', validators=[DataRequired()], id='omygod')
    submit = SubmitField('Submit')


class EditProfileForm(FlaskForm):
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('城市', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):
    email = StringField('邮箱', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('用户名', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                                                                    '用户名只包含字母、数字、.或_')])
    confirmed = BooleanField('是否完成邮箱验证')
    role = SelectField('角色', coerce=int)
    name = StringField('真实姓名', validators=['Length(0, 64'])
    location = StringField('城市', validators=['Length(0, 64)'])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已被注册')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已被注册')

class PostForm(FlaskForm):
    title = TextAreaField('标题', validators=[DataRequired()])
    body = TextAreaField('tell your story', validators=[DataRequired()])
    version_intro = TextAreaField()
    submit = SubmitField('提交')

class NewPostContentForm(FlaskForm):
    body = TextAreaField('tell your story', validators=[DataRequired()])
    version_intro = TextAreaField()
    submit = SubmitField('提交')


class CommentForm(FlaskForm):
    body = StringField('发表你的看法', validators=[DataRequired()])
    submit = SubmitField('提交')


class MessageForm(FlaskForm):
    body = StringField('告诉ta...', validators=[DataRequired()])
    submit = SubmitField('发送')