from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField,\
                    TextAreaField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.game.roll_parser import validate_error, roll_msg

# --- Games ---

class CreateGameForm(FlaskForm):
    game_name = StringField('Game Name', validators=[DataRequired()])
    chapter_name = StringField('First Chapter Name', validators=[DataRequired()], default="1")
    scene_name = StringField('First Scene Name', validators=[DataRequired()], default="1")
    submit = SubmitField('Create Game')

class DeleteGameForm(FlaskForm):
    name = StringField('Type Game Name', validators=[DataRequired()])
    submit = SubmitField('Yes, Delete This Game Forever')

# --- Chapters ---

class CreateChapterForm(FlaskForm):
    chapter_name = StringField('Chapter Name', validators=[DataRequired()])
    scene_name = StringField('First Scene Name', validators=[DataRequired()], default="1")
    make_current = BooleanField('Make Current', default=True)
    submit = SubmitField('Create Chapter')

class EditChapterForm(FlaskForm):
    chapter_name = StringField('Chapter Name', validators=[DataRequired()])
    make_current = BooleanField('Make Current')
    submit = SubmitField('Submit')

# --- Scenes ----

class CreateSceneForm(FlaskForm):
    scene_name = StringField('Scene Name', validators=[DataRequired()])
    make_current = BooleanField('Make Current', default=True)
    submit = SubmitField('Create Chapter')

class EditSceneForm(FlaskForm):
    scene_name = StringField('Scene Name', validators=[DataRequired()])
    make_current = BooleanField('Make Current')
    submit = SubmitField('Submit')

# --- Posts ----

class EditPostForm(FlaskForm):
    speaker = SelectField('Speaker', choices=[])
    body = TextAreaField('Body')
    submit = SubmitField('Submit')

    def validate_body(self, field):
        try:
            self.body_rolled = roll_msg(field.data)
        except SyntaxError as E:
            raise ValidationError(E.args[0])



# --- Extras ---

class DeleteCSPForm(FlaskForm):
    confirm = BooleanField('This cannot be undone, please be sure...',
                           validators=[DataRequired()])
    delete = SubmitField('Delete')

# --- Characters ---

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
