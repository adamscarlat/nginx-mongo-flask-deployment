# nginx-mongo-flask-deployment
Deployment of a Flask API with a MongoDB backend behind an nginx server on AWS.

## Contents

1. [Setting up an EC2 Instance](#setting-up-an-ec2-instance)
2. [Configure MongoDB](#configuring-mongodb)
3. [Configure Nginx with Gunicorn](#configuring-nginx)
4. [Remote Development with VSCode](#remote-dev-with-vscode)


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

## Configuring MongoDB



## Configuring Nginx


