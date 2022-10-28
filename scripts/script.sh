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
echo "Install Mysql Client"
sudo apt-get install mysql-client -y
echo "Install Python Dependancy"
sudo apt update
sudo apt install python3-pip -y
cd ~
sudo pip3 install -r requirements.txt
echo "Install systemd"
sudo apt-get -y install systemd
sudo cp ~/scripts/python.service /lib/systemd/system/python.service
sudo chmod 777 /lib/systemd/system/python.service
