from flask import url_for, render_template, flash, redirect
from flask_login import current_user, login_required

from app import db
from app.game import bp
from app.models import Game, Character, Chapter, Scene
from app.game.forms import CreateGameForm, DeleteGameForm, CreateCharacterForm,\
                            DeleteCharacterForm, EditCharacterForm,\
                            CreateChapterForm, EditChapterForm,\
                            CreateSceneForm, EditSceneForm

@bp.route('/example')
def example():
    return "This Works too!"

# --- Games ---


@bp.route('/game/<gameid>')
def game(gameid):
    g = Game.query.get_or_404(gameid)
    if current_user.is_anonymous or ((not current_user in g.players) and (current_user!=g.owner)):
        return render_template('game/game.html', game=g)
    c = Character.query.filter_by(game=g, player=current_user)
    option_list = [n.name for n in c]
    return render_template('game/game_interactive.html', option_list=option_list, game=g, user=current_user)

@bp.route('/nuke_posts/<gameid>')
def nuke_posts(gameid):
    g = Game.query.get_or_404(gameid)
    if current_user.is_anonymous or ((not current_user in g.players) and (current_user!=g.owner)):
        flash("You can't do that...")
    else:
        for i,c in enumerate(g.chapters):
            for j,s in enumerate(c.scenes):
                for p in s.posts:
                    db.session.delete(p)
                if i != 0 or j != 0:
                    db.session.delete(s)
            if i != 0:
                db.session.delete(c)
        db.session.commit()
        flash('Posts nuked')
    return redirect(url_for('game.game', gameid=gameid))


@login_required
@bp.route('/create_game', methods=['GET', 'POST'])
def create_game():
    form = CreateGameForm()
    if form.validate_on_submit():
        game = Game(name=form.game_name.data, owner=current_user)
        chapter = Chapter(name=form.chapter_name.data, game=game)
        # game.current_chapter = chapter
        scene = Scene(name=form.chapter_name.data, chapter=chapter)
        # chapter.current_scene = scene
        db.session.add_all([game,chapter,scene])
        db.session.commit()
        game.ensure_has_current()
        flash('Congratulations, you created a game called "{}"!'.format(game.name))
        return redirect(url_for('game.game', gameid = game.id))
    return render_template('game/create_game.html', form=form)

@login_required
@bp.route('/delete_game/<gameid>', methods=['GET', 'POST'])
def delete_game(gameid):
    game = Game.query.get_or_404(gameid)
    if not game in current_user.owned_games:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = DeleteGameForm()
    if form.validate_on_submit():
        if game.name != form.name.data:
            flash('Incorrect game name, try again')
            return redirect(url_for('game.delete_game', gameid=game.id))
        for chapter in game.chapters:
            for scene in chapter.scenes:
                for post in scene.posts:
                    db.session.delete(post)
                db.session.delete(scene)
            db.session.delete(chapter)
        for DM in game.DMs:
            db.session.delete(DM)
        db.session.delete(game)
        db.session.commit()
        flash('You deleted the game called "{}"!'.format(form.name.data))
        return redirect(url_for('auth.userpage', username = current_user.username))
    return render_template('game/delete_game.html', form=form, game=game)

# --- Chapters ---

@login_required
@bp.route('/game/<gameid>/create_chapter', methods=['GET', 'POST'])
def create_chapter(gameid):
    game = Game.query.get_or_404(gameid)
    if not game in current_user.owned_games:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = CreateChapterForm()
    if form.validate_on_submit():
        c = Chapter(name=form.chapter_name.data, game=game)
        s = Scene(name=form.scene_name.data, chapter=c)
        db.session.add_all([c,s])
        if form.make_current:
            game.current_chapter = c
        c.ensure_has_current() # has commit
        return redirect(url_for('game.game', gameid=gameid))
    return render_template('game/create_chapter.html', form=form, game=game)

@login_required
@bp.route('/game/<gameid>/chapter/<chapterid>', methods=['GET', 'POST'])
def chapter(gameid,chapterid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    if not game in current_user.owned_games:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditChapterForm()
    if form.validate_on_submit():
        chapter.name = form.chapter_name.data
        if form.make_current:
            game.current_chapter = chapter
            chapter.ensure_has_current() # has commit
        else:
            db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.chapter_name.data = chapter.name
        form.make_current.data = chapter.is_current
    return render_template('game/chapter.html', form=form, game=game, chapter=chapter)

# --- Scene ---

@login_required
@bp.route('/game/<gameid>/chapter/<chapterid>/create_scene', methods=['GET', 'POST'])
def create_scene(gameid,chapterid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    if not game in current_user.owned_games:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = CreateSceneForm()
    if form.validate_on_submit():
        s = Scene(name=form.scene_name.data, chapter=chapter)
        db.session.add(s)
        if form.make_current:
            chapter.current_scene = s
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    return render_template('game/create_scene.html', form=form, game=game, chapter=chapter)

@login_required
@bp.route('/game/<gameid>/chapter/<chapterid>/scene/<sceneid>', methods=['GET', 'POST'])
def scene(gameid,chapterid,sceneid):
    game = Game.query.get_or_404(gameid)
    chapter = Chapter.query.get_or_404(chapterid)
    scene = Scene.query.get_or_404(sceneid)
    if not game in current_user.owned_games:
        flash('Naughty!')
        return redirect(url_for('front.index'))
    form = EditSceneForm()
    if form.validate_on_submit():
        scene.name = form.scene_name.data
        if form.make_current:
            chapter.current_scene = scene
        db.session.commit()
        return redirect(url_for('game.game', gameid=gameid))
    else:
        form.scene_name.data = scene.name
        form.make_current.data = scene.is_current
    return render_template('game/scene.html', form=form, game=game, chapter=chapter, scene=scene)




# --- Characters ----

@login_required
@bp.route('/character/<characterid>', methods=['GET', 'POST'])
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

@login_required
@bp.route('/create_character', methods=['GET', 'POST'])
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

@login_required
@bp.route('/delete_character/<characterid>', methods=['GET', 'POST'])
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
