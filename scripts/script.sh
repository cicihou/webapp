#!/bin/bash
export DEBIAN_FRONTEND=noninteractive
echo 'debconf debconf/frontend select Noninteractive' | sudo debconf-set-selections
sudo apt-get install -y -q
echo "Install Nginx"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install nginx -y
sudo apt-get clean
sudo apt-get install dialog apt-utils -y
echo "Install Mysql"
sudo apt-get -y install mysql-server
sudo mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'mysql1234';"
sudo mysql --user=root --password=mysql1234 -e "create database webapp charset = utf8mb4;"
sudo service mysql restart
echo "Install Python Dependancy"
sudo apt update
sudo apt install python3-pip -y
cd ~
sudo pip3 install -r requirements.txt
python3 manage.py db stamp head
python3 manage.py db migrate
python3 manage.py db upgrade
echo "Install systemd"
sudo apt-get -y install systemd
sudo cp ~/scripts/python.service /lib/systemd/system/python.service
sudo chmod 777 /lib/systemd/system/python.service
sudo systemctl daemon-reload
sudo systemctl status python.service
sudo systemctl list-units
sudo systemctl enable python.service
sudo systemctl start python.service
sudo journalctl -u python.service
