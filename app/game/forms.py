from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField,\
                    TextAreaField
from wtforms.validators import DataRequired
from wtforms.widgets import Input

from app.models import Game


class CreateGameForm(FlaskForm):
    name = StringField('Game Name', validators=[DataRequired()])
    submit = SubmitField('Create Game')

class DeleteGameForm(FlaskForm):
    name = StringField('Type Game Name', validators=[DataRequired()])
    submit = SubmitField('Yes, Delete This Game Forever')

class CreateCharacterForm(FlaskForm):
    name = StringField('Character Name', validators=[DataRequired()])
    game = SelectField('Select Game', coerce = int)
    public = BooleanField('Make Character Visible?', default=True)
    submit = SubmitField('Create Character')

class EditCharacterForm(FlaskForm):
    game = SelectField('Game', coerce = int)
    public = BooleanField('Make Character Visible?', default=True)
    submit = SubmitField('Update Character')

class DeleteCharacterForm(FlaskForm):
    name = StringField('Type Character Name', validators=[DataRequired()])
    submit = SubmitField('Yes, Delete This Character Forever')
