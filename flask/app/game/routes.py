from flask import url_for, render_template, flash, redirect
from flask_login import current_user, login_required

from app import db
from app.game import bp
from app.models import Game, Character, Chapter, Scene, Post, User
from app.game.forms import CreateGameForm, EditGameForm, CreateCharacterForm,\
                            DeleteCharacterForm, EditCharacterForm,\
                            CreateChapterForm, EditChapterForm,\
                            CreateSceneForm, EditSceneForm,\
                            EditPostForm,\
                            ConfirmDeleteForm, ModifyPasswordForm,\
                            JoinGameForm

from app.game.events import set_currents

# --- Games ---

@bp.route('/games')
def games():
    game_list = Game.query.all()
    return render_template("game/games.html", game_list = game_list)


@bp.route('/game/<gameid>')
def game(gameid):
    g = Game.query.get_or_404(gameid)
    if current_user.is_anonymous or ((not current_user in g.players) and (current_user!=g.owner)):
        return render_template('game/game_viewer.html', game=g)
    c = Character.query.filter_by(game=g, player=current_user)
    option_list = [n.name for n in c]
    return render_template('game/game_interactive.html', option_list=option_list, game=g, user=current_user)

@bp.route('/join/<gameid>', methods=['GET', 'POST'])
@login_required
def join(gameid):
    g = Game.query.get_or_404(gameid)
    if g.has_member(current_user):
        return redirect(url_for('game.game',gameid=gameid))
    if g.is_full():
        flash("That game is already full!")
        return redirect(url_for('game.game',gameid=gameid))
    form = JoinGameForm(g)
    if form.validate_on_submit():
        c = Character(name=form.name.data,player=current_user,
                      game=g,public=form.visible.data)
        g.players.append(current_user)
        db.session.add(c)
        db.session.commit()
        flash('Welcome to the game!')
        return redirect(url_for('game.game',gameid=gameid))
    return render_template('game/join.html', game=g, form=form)

@bp.route('/game/<gameid>/abandon', methods=['GET', 'POST'])
@login_required
def abandon(gameid):
    return remove(gameid,user=current_user,boot=False)
@bp.route('/game/<gameid>/boot/<userid>', methods=['GET', 'POST'])
@login_required
def boot(gameid,userid):
    user = User.query.get_or_404(userid)
    return remove(gameid,user=user,boot=True)
def remove(gameid,user,boot):
    g = Game.query.get_or_404(gameid)
    if not g.has_player(user):
        return redirect(url_for('game.game',gameid=gameid))
    form = ConfirmDeleteForm()
    form.delete.label.text = ["Abandon","Boot"][boot]
    if form.validate_on_submit():
        g.remove_player(user)
        db.session.commit()
        return redirect(url_for('game.game',gameid=gameid))
    return render_template('game/'+ ["abandon","boot_player"][boot] +'.html', game=g,
                           form=form, player=user)

@bp.route('/create_game', methods=['GET', 'POST'])
@login_required
def create_game():
    form = CreateGameForm()
    if form.validate_on_submit():
        game = Game(name=form.game_name.data, owner=current_user,
                    blurb=form.blurb.data,player_max=form.get_player_max())
        game.set_password(form.password.data)
        chapter = Chapter(name=form.chapter_name.data, game=game)
        scene = Scene(name=form.chapter_name.data, chapter=chapter)
        db.session.add_all([game,chapter,scene])
        game.ensure_has_current()
        db.session.commit()
        set_currents(int(game.id))
        flash('Congratulations, you created a game called "{}"!'.format(game.name))
        return redirect(url_for('game.game', gameid = game.id))
    return render_template('game/create_game.html', form=form)

@bp.route('/edit_game/<gameid>', methods=['GET', 'POST'])
@login_required
def edit_game(gameid):
    game = Game.query.get_or_404(gameid)
    if not game.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditGameForm(game)
    player_list = game.players
    mform = ModifyPasswordForm()
    dform = ConfirmDeleteForm()
    if dform.delete.data and dform.validate_on_submit():
        game.empty() # remove all chapters, scenes, posts, etc
        for c in game.characters:
            db.session.delete(c) # remove all characters
        db.session.delete(game) # remove actual game
        db.session.commit()
        return redirect(url_for('auth.userpage', username = current_user.username))
    elif mform.change.data and mform.validate_on_submit():
        game.set_password(mform.password.data)
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    elif form.submit.data and form.validate_on_submit():
        game.name = form.name.data
        game.blurb = form.blurb.data
        game.player_max = form.get_player_max()
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.name.data = game.name
        form.blurb.data = game.blurb
        form.set_player_max(game.player_max)
        dform.confirm.data = False
    return render_template('game/edit_game.html', form=form, mform=mform,
                           dform=dform, game=game, player_list = player_list)

# --- Chapters ---

@bp.route('/game/<gameid>/create_chapter', methods=['GET', 'POST'])
@login_required
def create_chapter(gameid):
    game = Game.query.get_or_404(gameid)
    if not game.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = CreateChapterForm()
    if form.validate_on_submit():
        c = Chapter(name=form.chapter_name.data, game=game)
        s = Scene(name=form.scene_name.data, chapter=c)
        db.session.add_all([c,s])
        if form.make_current:
            game.current_chapter = c
        c.ensure_has_current()
        db.session.commit()
        set_currents(int(gameid))
        return redirect(url_for('game.game', gameid=gameid))
    return render_template('game/create_chapter.html', form=form, game=game)

@bp.route('/game/<gameid>/chapter/<chapterid>', methods=['GET', 'POST'])
@login_required
def chapter(gameid,chapterid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    if not chapter.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditChapterForm()
    dform = ConfirmDeleteForm()
    if form.submit.data and form.validate_on_submit():
        chapter.name = form.chapter_name.data
        if form.make_current:
            game.current_chapter = chapter
            chapter.ensure_has_current()
            db.session.commit()
            set_currents(int(gameid))
        else:
            db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    elif dform.delete.data and dform.validate_on_submit():
        chapter.empty()
        db.session.delete(chapter)
        if len(game.chapters) == 0:
            c = Chapter(name="1",game=game)
            db.session.add(c)
            game.current_chapter = c
            s = Scene(name="1",chapter=c)
            db.session.add(s)
            c.current_scene = s
        db.session.commit()
        set_currents(int(gameid))
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.chapter_name.data = chapter.name
        form.make_current.data = chapter.is_current
        dform.confirm.data = False
    return render_template('game/chapter.html', form=form, dform=dform,
                           game=game, chapter=chapter)

# --- Scene ---

@bp.route('/game/<gameid>/chapter/<chapterid>/create_scene', methods=['GET', 'POST'])
@login_required
def create_scene(gameid,chapterid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    if not chapter.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = CreateSceneForm()
    if form.validate_on_submit():
        s = Scene(name=form.scene_name.data, chapter=chapter)
        db.session.add(s)
        if form.make_current:
            chapter.current_scene = s
        db.session.commit()
        set_currents(int(gameid))
        return redirect(url_for('game.game', gameid=gameid))
    return render_template('game/create_scene.html', form=form, game=game, chapter=chapter)

@bp.route('/game/<gameid>/chapter/<chapterid>/scene/<sceneid>', methods=['GET', 'POST'])
@login_required
def scene(gameid,chapterid,sceneid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    scene = Scene.query.get_or_404(sceneid)
    if not scene.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditSceneForm()
    dform = ConfirmDeleteForm()
    if form.submit.data and form.validate_on_submit():
        scene.name = form.scene_name.data
        if form.make_current:
            chapter.current_scene = scene
        db.session.commit()
        set_currents(int(gameid))
        return redirect(url_for('game.game', gameid=gameid))
    elif dform.delete.data and dform.validate_on_submit():
        scene.empty()
        db.session.delete(scene)
        if len(chapter.scenes) == 0:
            s = Scene(name="1",chapter=chapter)
            db.session.add(s)
            chapter.current_scene = s
        db.session.commit()
        set_currents(int(gameid))
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.scene_name.data = scene.name
        form.make_current.data = scene.is_current
        dform.confirm.data = False
    return render_template('game/scene.html', form=form, dform=dform,
                           game=game, chapter=chapter, scene = scene)

# ---- Posts -----

@bp.route('/game/<gameid>/chapter/<chapterid>/scene/<sceneid>/post/<postid>', methods=['GET', 'POST'])
@login_required
def post(gameid,chapterid,sceneid,postid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    scene = Scene.query.get_or_404(sceneid)
    post = Post.query.get_or_404(postid)
    if not post.can_edit(current_user):
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditPostForm()
    dform = ConfirmDeleteForm()
    form.speaker.choices = [("Narrator", "Narrator")]\
                            + [(c.name,c.name) for c in game.characters if c.player.username == current_user.username]
    if form.submit.data and form.validate_on_submit():
        post.speaker = form.speaker.data
        post.body = form.body_rolled#.data
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    elif dform.delete.data and dform.validate_on_submit():
        db.session.delete(post)
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.speaker.data = post.speaker
        form.body.data = post.body
        dform.confirm.data = False
    return render_template('game/post.html', form=form, dform = dform, game = game,
                           chapter = chapter, scene = scene, post = post)


# --- Characters ----

@bp.route('/character/<characterid>', methods=['GET', 'POST'])
@login_required
def character(characterid):
    c = Character.query.get_or_404(characterid)
    if not c in current_user.owned_characters:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditCharacterForm()
    form.game.choices = [(0, "None")]+[(g.id, g.name) for g in current_user.owned_games+current_user.joined_games]
    if form.validate_on_submit():
        g = Game.query.get(form.game.data)
        c.game = g
        c.public = form.public.data
        db.session.commit()
        flash('Updated')
        return redirect(url_for('game.character', characterid = c.id))
    else:
        try:
            form.game.data = c.game.id
        except AttributeError:
            form.game.data = 0
        form.public.data = c.public
    return render_template('game/character.html', form=form, character=c)

@bp.route('/create_character', methods=['GET', 'POST'])
@login_required
def create_character():
    form = CreateCharacterForm()
    form.game.choices = [(0, "None")]+[(g.id, g.name) for g in current_user.owned_games+current_user.joined_games]
    if form.validate_on_submit():
        g = Game.query.get(form.game.data)
        c = Character(name=form.name.data, player=current_user,
                      game=g, public=form.public.data)
        db.session.add(c)
        db.session.commit()
        flash('Congratulations, you created a character called "{}"!'.format(c.name))
        return redirect(url_for('game.character', characterid = c.id))
    return render_template('game/create_character.html', form=form)

@bp.route('/delete_character/<characterid>', methods=['GET', 'POST'])
@login_required
def delete_character(characterid):
    c = Character.query.get_or_404(characterid)
    if not c in current_user.owned_characters:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = DeleteCharacterForm()
    if form.validate_on_submit():
        if c.name != form.name.data:
            flash('Incorrect character name, try again')
            return redirect(url_for('game.delete_character', characterid=c.id))
        db.session.delete(c)
        db.session.commit()
        flash('You deleted the character called "{}"!'.format(form.name.data))
        return redirect(url_for('auth.userpage', username = current_user.username))
    return render_template('game/delete_character.html', form=form, character=c)
