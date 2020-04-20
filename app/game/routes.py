from flask import url_for, render_template, flash, redirect
from flask_login import current_user, login_required

from app import db
from app.game import bp
from app.models import Game, Character
from app.game.forms import CreateGameForm, DeleteGameForm, CreateCharacterForm,\
                            DeleteCharacterForm, EditCharacterForm

@bp.route('/example')
def example():
    return "This Works too!"

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
        for p in g.posts:
            db.session.delete(p)
        db.session.commit()
        flash('Posts nuked')
    return redirect(url_for('game.game', gameid=gameid))


@login_required
@bp.route('/create_game', methods=['GET', 'POST'])
def create_game():
    form = CreateGameForm()
    if form.validate_on_submit():
        game = Game(name=form.name.data, owner=current_user)
        db.session.add(game)
        db.session.commit()
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
        for post in game.posts:
            db.session.delete(post)
        for DM in game.DMs:
            db.session.delete(DM)
        db.session.delete(game)
        db.session.commit()
        flash('You deleted the game called "{}"!'.format(form.name.data))
        return redirect(url_for('auth.userpage', username = current_user.username))
    return render_template('game/delete_game.html', form=form, game=game)

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
