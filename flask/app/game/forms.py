from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, BooleanField,\
                    TextAreaField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError

from app.models import Character, Game
from app.game.roll_parser import validate_error, roll_msg

# --- Games ---

class CreateGameForm(FlaskForm):
    game_name = StringField('Game Name', validators=[DataRequired()])
    blurb = TextAreaField('Summary', validators=[DataRequired()])
    chapter_name = StringField('First Chapter Name', validators=[DataRequired()], default="1")
    scene_name = StringField('First Scene Name', validators=[DataRequired()], default="1")
    password = PasswordField('Password (leave blank for none)')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    player_max = StringField('Player Max:', validators=[DataRequired()],
                             default="5")
    submit = SubmitField('Create Game')

    def get_player_max(self):
        try:
            return int(self.player_max.data)
        except (ValueError, TypeError):
            return None

    def validate_player_max(self, field):
        pm = self.get_player_max()
        if pm is None:
            raise ValidationError("Player max must be an integer")
        elif pm < 1:
            raise ValidationError("Player max must be positive")


class EditGameForm(FlaskForm):
    name = StringField('Game Name', validators=[DataRequired()])
    blurb = TextAreaField('Summary', validators=[DataRequired()])
    player_max = StringField('Player Max:', validators=[DataRequired()])
    submit = SubmitField('Submit')

    def __init__(self,game,*args,**kwargs):
        FlaskForm.__init__(self,*args,**kwargs)
        self.game = game

    def get_player_max(self):
        try:
            return int(self.player_max.data)
        except (ValueError, TypeError):
            return None
    def set_player_max(self,integer):
        self.player_max.data = str(integer)

    def validate_player_max(self, field):
        pm = self.get_player_max()
        if pm is None:
            raise ValidationError("Player max must be an integer")
        elif pm < 1:
            raise ValidationError("Player max must be positive")
        elif len(self.game.players) > pm:
            raise ValidationError(
                "Current player number ({}) exceeds desired player max".format(
                    len(self.game.players)
                )
            )

class JoinGameForm(FlaskForm):
    name = StringField('Character Name', validators=[DataRequired()])
    visible = BooleanField('Make Character Visible?',default=True)
    password = PasswordField('Game Password')
    submit = SubmitField('Join')

    def __init__(self,game,*args,**kwargs):
        FlaskForm.__init__(self,*args,**kwargs)
        self.game = game

    def validate_name(self,field):
        if field.data in [c.name for c in self.game.characters]:
            raise ValidationError("Character Name Already in Use")

    def validate_password(self,field):
        if not self.game.check_password(field.data):
            raise ValidationError("Incorrect Password")

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

class ConfirmDeleteForm(FlaskForm):
    confirm = BooleanField('This cannot be undone, please be sure...',
                           validators=[DataRequired()])
    delete = SubmitField('Delete')

class ModifyPasswordForm(FlaskForm):
    password = PasswordField('New Password')
    password2 = PasswordField(
        'Repeat Password', validators=[EqualTo('password')])
    change = SubmitField('Change Password')

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
