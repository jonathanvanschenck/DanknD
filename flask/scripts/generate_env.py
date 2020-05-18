import uuid
from sys import argv

config = {
    "FLASK_APP":"wsgi.py"
}

try:
    value = argv[1]
except IndexError:
    value = "development"

if value.lower() == "production":
    config.update({"DATABASE_URL":"postgresql://flask_user:flask_password@db-app:5432/flask_db"})


with open(".env","w") as f:
    f.write("SECRET_KEY="+str(uuid.uuid4().hex)+"\n")
    for k,v in config.items():
        f.write(k+"="+v+"\n")
    # msg = input("Specify mail server (default smtp.gmail.com): ")
    # if msg == "":
    #     f.write("MAIL_SERVER=smtp.gmail.com\n")
    # else:
    #     f.write("MAIL_SERVER="+msg+"\n")
    # msg = input("Specify mail server (default smtp.gmail.com): ")
    # if msg == "":
    #     f.write("MAIL_SERVER=smtp.gmail.com\n")
    # else:
    #     f.write("MAIL_SERVER="+msg+"\n")
    # msg = input("Specify mail port (default 587): ")
    # if msg == "":
    #     f.write("MAIL_PORT=587\n")
    # else:
    #     f.write("MAIL_PORT="+msg+"\n")
    #
    # f.write("MAIL_USE_TLS=True\n")
    #
    # msg = input("Specify email (you@example.com): ")
    # f.write("MAIL_USERNAME="+msg+"\n")
    # f.write("MAIL_PASSWORD="+msg+"\n")
