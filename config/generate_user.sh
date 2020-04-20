echo "from app import db" > temp
echo "from app.models import User" >> temp

read -p "Choose Username: " usrname

echo "u = User('$usrname')" >> temp

read -s -p "Choose Admin Password: " psword

echo "u.set_password('$psword')" >> temp
echo "db.session.add(u)" >> temp
echo "db.session.commit()" >> temp

cat temp | ./venv/bin/flask shell

rm temp
