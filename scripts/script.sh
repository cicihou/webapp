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
sudo cp ~/scripts/m.service /lib/systemd/system/m.service
sudo chmod 777 /lib/systemd/system/m.service
echo "cloud watch"
sudo wget https://s3.us-east-1.amazonaws.com/amazoncloudwatch-agent-us-east-1/ubuntu/amd64/latest/amazon-cloudwatch-agent.deb
sudo dpkg -i -E ./amazon-cloudwatch-agent.deb
sudo touch /var/log/csye6225.log
sudo chmod 777 /var/log/csye6225.log
sudo cp ~/scripts/cloudwatch-config.json /opt/cloudwatch-config.json
sudo chmod 777 /opt/cloudwatch-config.json
echo "config cloud watch agent"
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a fetch-config -m ec2 -c file:/opt/cloudwatch-config.json -s
