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
#sudo apt-get install debconf-utils
#sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password password mysql1234'
#sudo debconf-set-selections <<< 'mysql-server mysql-server/root_password_again password mysql1234'
sudo apt-get -y install mysql-server
sudo mysql -u root -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH caching_sha2_password BY 'mysql1234';"
sudo mysql --user=root --password=mysql1234 -e "create database webapp charset = utf8mb4;"
sudo service mysql restart
echo "Install Python"
cd /tmp
sudo apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev libgdbm-dev libnss3-dev libedit-dev libc6-dev
wget https://www.python.org/ftp/python/3.6.15/Python-3.6.15.tgz
tar -xzf Python-3.6.15.tgz
cd Python-3.6.15
./configure --enable-optimizations --with-lto
sudo make -j 1
sudo make altinstall
echo finish python install
sudo apt install python3-pip -y
cd ~
python3.6 -m pip install -r requirements.txt
python3.6 manage.py db stamp head
python3.6 manage.py db migrate
python3.6 manage.py db upgrade
echo "Install systemd"
sudo apt-get -y install systemd
sudo cp ~/scripts/python.service /lib/systemd/system/python.service
sudo systemctl daemon-reload
sudo systemctl enable /lib/systemd/system/python.service
sudo systemctl start /lib/systemd/system/python.service
