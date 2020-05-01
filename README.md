# DanknD
A Play-by-Post framework for D&amp;D 5e


# Development
## Set Up (Linux)
```bash
 $ python3 -m venv venv
 $ source venv/bin/activate
 (venv) $ pip install -r requirements.txt
 $ python config/generate_env.py
 $ ./config/setup_db.sh
```

## Set Up (Windows)

```cmd
 (venv) > flask db init
 (venv) > flask db migrate -m 'Set Up'
 (venv) > flask db upgrade
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
 - [ ] refactor for docker support
 - [ ] refactor routes and forms to follow a better "inheritance" structure
 - [ ] find a way to stick the models.py into a subfolder to better separate concerns
 - [ ] refactor routes a models to more consistently separate concerns (add more and better methods to models)
 - [ ] find a better organizational structure for the html templates
