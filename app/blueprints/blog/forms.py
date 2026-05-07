from flask_wtf import FlaskForm
from wtforms import TextAreaField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length


class CommentForm(FlaskForm):
    """Comment submission form."""
    
    body = TextAreaField('Comment', validators=[
        DataRequired(message='Comment cannot be empty.'),
        Length(min=1, max=2000, message='Comment must be between 1 and 2000 characters.')
    ])
    parent_id = HiddenField()  # For threaded replies
    submit = SubmitField('Post Comment')


class SearchForm(FlaskForm):
    """Search form."""
    
    q = StringField('Search', validators=[
        DataRequired(message='Please enter a search term.'),
        Length(min=1, max=100, message='Search term must be between 1 and 100 characters.')
    ])
    submit = SubmitField('Search')