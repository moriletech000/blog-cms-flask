from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional
from app.models.category import Category


class PostForm(FlaskForm):
    """Post creation/editing form."""
    
    title = StringField('Title', validators=[
        DataRequired(message='Title is required.'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters.')
    ])
    body = TextAreaField('Body', validators=[
        DataRequired(message='Post body is required.')
    ])
    excerpt = TextAreaField('Excerpt', validators=[
        Optional(),
        Length(max=500, message='Excerpt must be less than 500 characters.')
    ])
    cover_image = FileField('Cover Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Images only!')
    ])
    category_id = SelectField('Category', coerce=str, validators=[Optional()])
    tags = StringField('Tags', validators=[
        Optional(),
        Length(max=200, message='Tags must be less than 200 characters.')
    ])
    status = SelectField('Status', choices=[
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], default='draft')
    submit = SubmitField('Save Post')
    
    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        # Populate category choices
        self.category_id.choices = [('', 'No Category')] + [
            (str(cat.id), cat.name) for cat in Category.query.order_by(Category.name).all()
        ]


class CategoryForm(FlaskForm):
    """Category creation/editing form."""
    
    name = StringField('Name', validators=[
        DataRequired(message='Category name is required.'),
        Length(min=1, max=100, message='Name must be between 1 and 100 characters.')
    ])
    description = StringField('Description', validators=[
        Optional(),
        Length(max=255, message='Description must be less than 255 characters.')
    ])
    color = StringField('Color', validators=[
        DataRequired(message='Color is required.'),
        Length(min=7, max=7, message='Color must be a valid hex code (e.g., #6366f1).')
    ], default='#6366f1')
    submit = SubmitField('Save Category')


class UserEditForm(FlaskForm):
    """User editing form for admin."""
    
    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=20, message='Username must be between 3 and 20 characters.')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Length(max=120, message='Email must be less than 120 characters.')
    ])
    role = SelectField('Role', choices=[
        ('reader', 'Reader'),
        ('editor', 'Editor'),
        ('admin', 'Admin')
    ])
    is_active = SelectField('Status', choices=[
        ('True', 'Active'),
        ('False', 'Inactive')
    ], coerce=lambda x: x == 'True')
    bio = TextAreaField('Bio', validators=[
        Optional(),
        Length(max=500, message='Bio must be less than 500 characters.')
    ])
    submit = SubmitField('Update User')


class CommentModerationForm(FlaskForm):
    """Comment moderation form."""
    
    action = HiddenField()
    comment_id = HiddenField()
    submit = SubmitField('Update')