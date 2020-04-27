from flask import current_app, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login

# ---- Helper Functions ----

@login.user_loader
def load_user(id):
    return User.query.get(int(id))


# ---- Tables ----

joinedgames = db.Table('joinedgames',
    db.Column('game_id',db.Integer,db.ForeignKey('game.id'),primary_key=True),
    db.Column('user_id',db.Integer,db.ForeignKey('user.id'),primary_key=True)
)


# I think these are extranious, since they are both one-to-many relationships...
ownedcharacters = db.Table('ownedcharacters',
    db.Column('user_id',db.Integer,db.ForeignKey('user.id'),primary_key=True),
    db.Column('character_id',db.Integer,db.ForeignKey('character.id'),primary_key=True)
)

# I think these are extranious, since they are both one-to-many relationships...
allcharacters = db.Table('allcharacters',
    db.Column('game_id',db.Integer,db.ForeignKey('game.id'),primary_key=True),
    db.Column('character_id',db.Integer,db.ForeignKey('character.id'),primary_key=True)
)

allchapters = db.Table('allchapters',
    db.Column('game_id',db.Integer,db.ForeignKey('game.id'),primary_key=True),
    db.Column('chapter_id',db.Integer,db.ForeignKey('chapter.id'),primary_key=True)
)

allscenes = db.Table('allscenes',
    db.Column('chapter_id',db.Integer,db.ForeignKey('chapter.id'),primary_key=True),
    db.Column('scene_id',db.Integer,db.ForeignKey('scene.id'),primary_key=True)
)

# ---- Objects ----

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))


    owned_games = db.relationship('Game',back_populates='owner',lazy=True)

    joined_games = db.relationship('Game', secondary=joinedgames, lazy=True,
                                   back_populates='players')

    owned_characters = db.relationship('Character', secondary=ownedcharacters,
                                          lazy=True, back_populates='player')

    posts = db.relationship('Post', back_populates = 'poster', lazy = True)

    # backref creates:
    #  sent_DMs
    #  received_DMs


    def __init__(self,username,email=None):
        self.username = username
        if email is None:
            self.email = username+"@example.com"
        else:
            self.emial = email

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique = True, index = True)
    public = db.Column(db.Boolean, default=True)

    player = db.relationship('User', secondary=ownedcharacters,
                             lazy=True, uselist=False,
                             back_populates='owned_characters')

    game = db.relationship('Game', secondary=allcharacters,
                             lazy=True, uselist=False,
                             back_populates='characters')

    def __repr__(self):
        return '<Character: {0} | {1}>'.format(self.id,self.name)

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default="New Game")

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'),nullable=False)
    owner = db.relationship('User',back_populates='owned_games',lazy=True,
                            uselist=False)

    players = db.relationship('User', secondary=joinedgames, lazy=True,
                              back_populates='joined_games')

    characters = db.relationship('Character', secondary=allcharacters,
                                 lazy=True, back_populates='game')

    chapters = db.relationship('Chapter', secondary=allchapters,
                               lazy = True, back_populates='game',
                               uselist = True)

    current_chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id'),index=True)
    current_chapter = db.relationship("Chapter", lazy=True, uselist = False,
                                      foreign_keys=[current_chapter_id])

    # backref creates:
    #  DMs

    @property
    def current_scene(self):
        try:
            return self.current_chapter.current_scene
        except AttributeError:
            return None

    def __repr__(self):
        return '<Game: {0} | {1}>'.format(self.id,self.name)

    def ensure_has_current(self):
        if self.current_chapter is None:
            try:
                last_chapter = self.chapters[-1]
            except IndexError as E:
                raise KeyError("Game has no chapters") from E
            self.current_chapter = last_chapter
        self.current_chapter.ensure_has_current()

    def empty(self):
        for c in self.chapters:
            c.empty()
            db.session.delete(c)


class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default="New Chapter")

    game = db.relationship("Game", secondary=allchapters,
                           back_populates = "chapters", lazy=True,
                           uselist=False)

    scenes = db.relationship('Scene', secondary=allscenes,
                               lazy = True, back_populates='chapter',
                               uselist = True)

    current_scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'),index=True)
    current_scene = db.relationship("Scene", lazy=True, uselist = False,
                                      foreign_keys=[current_scene_id])

    @property
    def is_current(self):
        try:
            return self is self.game.current_chapter
        except AttributeError:
            return False

    def __repr__(self):
        return '<Chapter: {0} | {1} for {2}>'.format(self.id,self.name,self.game.name)

    # def to_HTML(self):
    #     return '''<div class="card md-6 bg-danger chapter-card" id="{outer_id}">
    #         <div class="card-body chapter-card-body" id="{inner_id}">
    #             <h2 class="card-title">
    #                 <span class="text-muted">Chapter: </span>{name}
    #                 <span style="float: right;">
    #                     <a href="{url_edit}">Edit</a>
    #                     <a href="{url_add}">Add Scene</a>
    #                 </span>
    #             </h2>
    #         </div>
    #     </div>'''.format(
    #         name = self.name,
    #         outer_id = self.get_outer_HTML_id(),
    #         inner_id = self.get_inner_HTML_id(),
    #         url_edit = url_for('game.chapter', gameid=self.game.id, chapterid=self.id),
    #         url_add = url_for('game.create_scene', gameid=self.game.id, chapterid=self.id)
    #     )

    def to_HTML(self):
        return '''<div class="chapter-card" id="{outer_id}">
            <div class="chapter-card-body" id="{inner_id}">
                <span class="text-muted">Chapter: </span>{name}
                <span style="float: right;">
                    <a href="{url_edit}">Edit</a>
                    <a href="{url_add}">Add Scene</a>
                </span>
            </div>
        </div>'''.format(
            name = self.name,
            outer_id = self.get_outer_HTML_id(),
            inner_id = self.get_inner_HTML_id(),
            url_edit = url_for('game.chapter', gameid=self.game.id, chapterid=self.id),
            url_add = url_for('game.create_scene', gameid=self.game.id, chapterid=self.id)
        )

    def get_outer_HTML_id(self):
        return "chapter-card-id-{}".format(self.id)

    def get_inner_HTML_id(self):
        return "chapter-card-body-id-{}".format(self.id)

    def ensure_has_current(self):
        if self.current_scene is None:
            try:
                last_scene = self.scenes[-1]
            except IndexError as E:
                raise KeyError("Chapter has no scenes") from E
            self.current_scene = last_scene
        db.session.commit()

    def empty(self):
        for s in self.scenes:
            s.empty()
            db.session.delete(s)


class Scene(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), default="New Scene")

    chapter = db.relationship("Chapter", secondary=allscenes,
                               back_populates = "scenes", lazy=True,
                               uselist=False)

    posts = db.relationship('Post', back_populates = 'scene', lazy = True)

    @property
    def game(self):
        try:
            return self.chapter.game
        except AttributeError:
            return None

    @property
    def is_current(self):
        try:
            return self is self.chapter.current_scene
        except AttributeError:
            return False

    def __repr__(self):
        return '<Scene: {0} | {1} for {2}>'.format(self.id,self.name,self.chapter.name)

    # def to_HTML(self):
    #     return '''<div class="card md-6 bg-warning scene-card" id="{outer_id}">
    #         <div class="card-body scene-card-body" id="{inner_id}">
    #             <h3 class="card-title">
    #                 <span class="text-muted">Scene: </span>{name}
    #                 <span style="float: right;">
    #                     <a href="{url_edit}">Edit</a>
    #                 </span>
    #             </h3>
    #         </div>
    #     </div>'''.format(
    #         name = self.name,
    #         outer_id = self.get_outer_HTML_id(),
    #         inner_id = self.get_inner_HTML_id(),
    #         url_edit = url_for('game.scene', gameid=self.chapter.game.id, chapterid=self.chapter.id, sceneid=self.id)
    #     )

    def to_HTML(self):
        return '''<div class="scene-card" id="{outer_id}">
            <div class="scene-card-body" id="{inner_id}">
                <span class="text-muted">Scene: </span>{name}
                <span style="float: right;">
                    <a href="{url_edit}">Edit</a>
                </span>
            </div>
        </div>'''.format(
            name = self.name,
            outer_id = self.get_outer_HTML_id(),
            inner_id = self.get_inner_HTML_id(),
            url_edit = url_for('game.scene', gameid=self.chapter.game.id, chapterid=self.chapter.id, sceneid=self.id)
        )

    def get_outer_HTML_id(self):
        return "scene-card-id-{}".format(self.id)

    def get_inner_HTML_id(self):
        return "scene-card-body-id-{}".format(self.id)

    def empty(self):
        for p in self.posts:
            db.session.delete(p)
# ---- Associations ----

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    speaker = db.Column(db.String(64))
    body = db.Column(db.String(128))

    poster_id = db.Column(db.Integer, db.ForeignKey('user.id'),index=True)
    poster = db.relationship("User", back_populates = "posts", lazy=True)

    scene_id = db.Column(db.Integer, db.ForeignKey('scene.id'),index=True)
    scene = db.relationship("Scene", back_populates = "posts", lazy=True)

    @property
    def game(self):
        try:
            return self.scene.chapter.game
        except AttributeError:
            return None

    def __repr__(self):
        return '<Post: {0} in scene {1} by {2}>'.format(self.id,self.scene.id,self.poster.username)

    # def to_HTML(self):
    #     return '''<div class="card md-6 bg-{bgtype} post-card" id="{outer_id}">
    #         <div class="card-body post-card-body" id="{inner_id}">
    #             <h5 class="card-title">{speaker} <span class="text-muted">({poster})</span></h5>
    #             <p class="card-text post-card-text" id="{text_id}">{body}</p>
    #         </div>
    #     </div>'''.format(
    #         speaker = self.speaker,
    #         bgtype = ["success","info"][self.speaker=="Narrator"],
    #         poster = self.poster.username,
    #         body = self.body,
    #         outer_id = self.get_outer_HTML_id(),
    #         inner_id = self.get_inner_HTML_id(),
    #         text_id = self.get_text_HTML_id()
    #     )

    def to_HTML(self):
        try:
            sid = self.scene.id
            cid = self.scene.chapter.id
            gid = self.scene.chapter.game.id
            edit_url = url_for('game.post',gameid=gid,chapterid=cid,sceneid=sid,postid=self.id)
        except AttributeError:
            edit_url = "#"
        return '''<div class="post-card post-type-{type}" id="{outer_id}">
            <div class="post-card-body" id="{inner_id}">
                <div class="post-card-title">
                    {speaker} <span class="text-muted">({poster})</span>
                    <span style="float: right;"><a href="{edit_url}">Edit</a></span>
                </div>
                <p class="post-card-text post-text-type-{type}" id="{text_id}">{body}</p>
            </div>
        </div>'''.format(
            speaker = self.speaker,
            type = ["speech","narration"][self.speaker=="Narrator"],
            poster = self.poster.username,
            body = self.body,
            outer_id = self.get_outer_HTML_id(),
            inner_id = self.get_inner_HTML_id(),
            text_id = self.get_text_HTML_id(),
            edit_url = edit_url
        )

    def get_outer_HTML_id(self):
        return "post-card-id-{}".format(self.id)

    def get_inner_HTML_id(self):
        return "post-card-body-id-{}".format(self.id)

    def get_text_HTML_id(self):
        return "post-card-text-id-{}".format(self.id)

class DM(db.Model):
    __tablename__= 'dm'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))

    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'),index=True)
    sender = db.relationship("User", backref = "sent_DMs", lazy=True,
                             foreign_keys=[sender_id])
    #
    to_id = db.Column(db.Integer, db.ForeignKey('user.id'),index=True)
    to = db.relationship("User", backref = "received_DMs", lazy=True,
                             foreign_keys=[to_id])
    #
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'),index=True)
    game = db.relationship("Game", backref = "DMs", lazy=True)

    def __repr__(self):
        return '<DM: {0} in game {1} by {2} to {3}>'.format(
            self.id,
            self.game.id,
            self.sender.username,
            self.to.username
        )
