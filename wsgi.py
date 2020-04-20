from app import create_app

if __name__ == "__main__":
    create_app().run('localhost', 8000, debug = True)
