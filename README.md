# DanknD
A Play-by-Post framework for D&amp;D 5e

# Set Up
```bash
 $ python3 -m venv venv
 $ source venv/bin/activate
 (venv) $ pip install -r requirements.txt
 $ python config/generate_env.py
 $ ./config/setup_db.sh
```


# Running

```bash
 (venv) $ gunicorn wsgi:"create_app()" --worker-class eventlet --bind localhost:8000
```


# Set Up (Windows)

```cmd
 (venv) > flask db init
 (venv) > flask db migrate -m "Set Up"
 (venv) > flask db upgrade
```
