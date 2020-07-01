# DanknD
A Play-by-Post framework for D&amp;D 5e based on `flask`, `postgres` and `nginx`

# Usage
## Set Up
Usage currently requires `docker-compose`. Simply run:
```bash
 $ docker-compose build
 $ docker-compose up
```
If this is your first time (or if you nuked the database as explained in the clean up section), then part of setup will generate a new admin account with the password: "guessme". YOU SHOULD CHANGE THIS IMMEDIATELY, but hey, if you want any old rando to be able to access your admin account, don't let me tell you how to live your life.

## Clean up
```bash
 $ docker-compose down
```
If you also want to nuke the database, run:
```bash
 $ docker volume prune
```
Be careful, though, because this will also delete any other volumes that are not currently being used on your system

# Development
## Set Up (Linux)
```bash
 $ cd flask
 $ python3 -m venv venv
 $ source venv/bin/activate
 (venv) $ pip install -r requirements.txt
 (venv) $ python scripts/generate_env.py development
 (venv) $ flask db init
 (venv) $ flask db migrate -m 'setup'
 (venv) $ flask db upgrade
 (venv) $ python manager.py user-health-check
 (venv) $ python manager.py user-add YOUR_NEW_USER_HERE
```

## Running

```bash
 (venv) $ gunicorn wsgi:"create_app()" --worker-class eventlet --bind localhost:8000
```

# To do
 - [ ] comment everything . . .
 - [ ] Add a busy gif to the game page to show socket.io is loading
 - [ ] set up email support
 - [ ] set up user password reset
 - [ ] make user page nicer
 - [ ] think about how to handle notifications (about posts, DMs, etc)
 - [ ] add DM support
 - [ ] add more player modification support in game.edit_game -- it looks awful
 - [x] refactor for docker support
 - [ ] refactor routes and forms to follow a better "inheritance" structure
 - [ ] find a way to stick the models.py into a subfolder to better separate concerns
 - [ ] refactor routes a models to more consistently separate concerns (add more and better methods to models)
 - [ ] find a better organizational structure for the html templates
 - [ ] Add a how to page
