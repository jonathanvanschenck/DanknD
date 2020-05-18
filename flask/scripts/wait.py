import socket
import time
import os

host = os.environ.get("SQL_HOST") # db-app
port = int(os.environ.get("SQL_PORT")) # 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    # Attempt to connect to the postgres server
    try:
        s.connect((host,port))
        s.close()
        break
    except socket.error as ex:
        print("Still waiting . . .")
        time.sleep(1.0)
