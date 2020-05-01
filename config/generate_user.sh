#!/usr/bin/env bash

read -p "Choose Username: " usrname
read -s -p "Choose Admin Password: " psword
echo ""
read -p "Add more users? (y/N) " yn

echo "from app import db" > temp
echo "from app.models import User" >> temp
echo "u = User('$usrname')" >> temp
echo "u.set_password('$psword')" >> temp
echo "db.session.add(u)" >> temp
echo "db.session.commit()" >> temp

cat temp | ./venv/bin/flask shell

rm temp

if [ "$yn" = "y" ] || [ "$yn" = "Y" ]; then
  ./config/generate_user.sh
fi
