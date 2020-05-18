# Handles the CLI for flask, allows db to be configured according to the
#

import click
from flask.cli import FlaskGroup, with_appcontext

from app import create_app, db
from app.models import User

# Get a reference to the flask cli
@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    pass

# Attach a user health check option
@cli.command('user-health-check', short_help="Check health of db User table")
@with_appcontext
def user_health_check():
    # Checks if db has no users, and if so generates an admin account
    click.echo("Using database: "+str(db))
    if len(User.query.all()) == 0:
        click.echo("No admin account detected, creating now . . .")
        u = User("admin")
        u.set_password("guessme")
        db.session.add(u)
        db.session.commit()
    else:
        click.echo("admin account detected")

# Attach a add user options for easy cli
@cli.command('user-add', short_help="Add new user to db")
@click.argument('username')
@click.option('-e','--email',default=None)
@click.option('--password', prompt=True, hide_input=True,
              confirmation_prompt=True)
@with_appcontext
def user_add(username,email,password):
    if email is None:
        u = User(username)
    else:
        u = User(username,email)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()


if __name__ == '__main__':
    # Run the flask cli object
    cli()
