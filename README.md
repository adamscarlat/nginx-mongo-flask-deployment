# nginx-mongo-flask-deployment
Deployment of a Flask API with a MongoDB backend behind an nginx server on AWS.

## Contents

1. [Setting up an EC2 Instance](#setting-up-an-ec2-instance)
2. [Installs] (#Installs)
3. [Configure MongoDB](#configuring-mongodb)
4. [Configure Nginx with Gunicorn](#configuring-nginx)
5. [Remote Development with VSCode](#remote-dev-with-vscode)


## Setting up an EC2 Instance
Start an EC2 instance with an Ubuntu 16.04 OS on AWS. Make sure a security group that accepts SSH is enabled. Make sure to have a .pem file for login or generate a new one. 
To have the instance accept the pem file it must have a root read-only permission. On a linux based OS, make the following changes to the pem file:

```
chmod 400 PEM_FILE.pem
```

Once the instance is running SSH into it:

```
ssh -i PEM_FILE.pem ubuntu@AWS_IP_ADDRESS
```

__Optionally__, it is possible to map the pem file to the ip address in the host file. 

First copy the file to the ssh folder:
```
mv ~/Downloads/PEM_FILE.pem ~/.ssh
```

Open the shh config file for editing: `vim ~/.ssh/config` and add the following,

```
Host *amazonaws.com
IdentityFile ~/.ssh/PEM_FILE.pem
User ubuntu
```
Now sshing into the machine is simpler:

```
ssh AWS_IP_ADDRESS
```

## Installs

Now we need to get all the packages necessary to run the database, web server and the API.

1. Python3 and pip
```
sudo apt-get install python3-pip
```

2. Virtual Env for Python

```
sudo pip3 install virtualenv
```

Create a virtual environment and activate it:

```
mkdir ~/PROJECT_NAME
cd ~/PROJECT_NAME
virtualenv PROJECT_NAME_env
source PROJECT_NAME_env/bin/activate
```

3. (in virtual env) Install gunicorn and flask:

```
pip3 install gunicorn flask
```
Set up the flask main file to run on host 0.0.0.0 port 5000 (default port)

Create a wsgi file
This is a Web Server Gateway Interface and it will be used by gunicorn and the web server (nginx) to interface with our web application (flask). Create the new wsgi file and add the text:

`vi ~/PROJECT_NAME/wsgi.py`
```
from MY_PROJECT_NAME import app

if __name__ == "__main__":
    app.run()
```
4. Test Gunicorn
```
cd ~/PROJECT_NAME
gunicorn --bind 0.0.0.0:5000 wsgi:app
curl -X GET ec2-18-217-231-215.us-east-2.compute.amazonaws.com:5000
```
5. Deactivate the virtual environment: `deactivate`

## Configuring MongoDB



## Configuring Nginx


