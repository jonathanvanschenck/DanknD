rm app.db
rm -r migrations

read -s -p "Choose Admin Password: " psword

./venv/bin/flask db init
./venv/bin/flask db migrate -m "Set Up"
./venv/bin/flask db upgrade


echo "from app import db" > temp
echo "from app.models import User" >> temp
echo "u = User('admin')" >> temp
echo "u.set_password('$psword')" >> temp
echo "db.session.add(u)" >> temp
echo "db.session.commit()" >> temp

cat temp | ./venv/bin/flask shell

rm temp
