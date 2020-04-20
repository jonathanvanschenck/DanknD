import uuid
import os
# from app.models import User
# from app import db


if os.path.isfile(".env"):
    if input("environment file already exists, override it? (Y/n)").lower() != "n":
        with open(".env","w") as f:
            f.write("SECRET_KEY="+str(uuid.uuid4().hex)+"\n")
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
