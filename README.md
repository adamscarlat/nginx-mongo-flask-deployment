# nginx-mongo-flask-deployment
Deployment of a Flask API with a MongoDB backend behind an nginx server on AWS.

## Contents

1. [Setting up an EC2 Instance](#setting-up-an-ec2-instance)
2. [Installs and Configurations](#installs-and-configurations)
4. [Installing and Configuring Nginx](#installing-and-configuring-nginx)
5. [Remote Development with VSCode](#remote-development-with-vscode)


## Setting up an EC2 Instance
Start an EC2 instance with an Ubuntu 16.04 OS on AWS. Make sure a security group that accepts SSH and HTTP is enabled. Make sure to have a .pem file for login or generate a new one. 
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

## Installs and Configurations

Now we need to get all the packages necessary to run the database, web server and the API.
First update apt:

```
sudo apt-get update
```

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
curl -X GET AWS_DOMAIN:5000
```
This will get to the root (/) url of your API. If there is no controller handling that url send the request to a valid url. You should get a response from your API at this point. 

Deactivate the virtual environment: `deactivate`

5. Make Gunicorn a system service 

Now we make Gunicorn a service process that will run as a startup daemon process. Unlike nginx and mongo, it does not come with a systemd unit file (required by linux if you want to be a service) so we'll create one for it.

`sudo vi /etc/systemd/system/PROJECT_NAME.service`

```
    [Unit]
    Description=Gunicorn instance to serve PROJECT_NAME
    After=network.target

    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/PROJECT_NAME
    Environment="PATH=/home/ubuntu/PROJECT_NAME/PROJECT_NAME_env/bin"
    ExecStart=/home/ubuntu/PROJECT_NAME/PROJECT_NAME_env/bin/gunicorn --workers 3 --bind unix:PROJECT_NAME.sock -m 007 wsgi:app

    [Install]
    WantedBy=multi-user.target
```
Start and enable this service:
```
sudo systemctl start PROJECT_NAME
sudo systemctl enable PROJECT_NAME
```

6. Install MongoDB

GPG keys are required by apt to ensure this package's consistency
```
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv EA312927
```
Create a MongoDB list file in /etc/apt/sources.list.d/
```
echo "deb http://repo.mongodb.org/apt/ubuntu xenial/mongodb-org/3.2 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.2.list
```
Get mongo
```
sudo apt-get install -y mongodb-org
```

Now we start mongo and enable it so that it will run as a startup daemon process:
```
sudo systemctl start mongod
sudo systemctl enable mongodb
sudo systemctl status mongodb
```

Test MongoDB
```
mongo
show dbs
```


## Installing and Configuring Nginx

Install nginx
```
sudo apt-get install nginx
```

Configure Nginx to work with Gunicorn wsgi

Create a file for a nginx website and add the following text. Replace project name and server domain with yours
```
sudo nano /etc/nginx/sites-available/PROJECT_NAME
```

```
    server {
        listen 80;
        server_name SERVER_DOMAIN_GOES_HERE;

        location / {
            include proxy_params;
            proxy_pass http://unix:///home/ubuntu/PROJECT_NAME/PROJECT_NAME.sock;
        }
    }
```
This will make nginx forward any requests made to our aws domain on port 80 to PROJECT_NAME_.sock. Gunicorn listens on this socket and through interprocess communication it will receive the http request and route it to the web app.

Create a symbolic link to the root sites-enabled folder:
```
sudo ln -s /etc/nginx/sites-available/MY_PROJECT_NAME /etc/nginx/sites-enabled
```

Check the nginx configuration for any syntax errors:
```
sudo nginx -t
```

*At this point* you are most likely to run into an error. Nginx may complain that the domain name (aws default domain name) is too long. Fix this by going to the nginx.conf and change the `server_name_hash_bucket_size` to next power of 2 (also uncomment). nginx conf file is located at: `/etc/nginx/nginx.conf`.

Run Nginx: 
```
sudo systemctl restart nginx
```

Test 
```
curl -X GET curl -X GET AWS_DOMAIN
````

## Remote Development with VSCode
This is a nice feature which allows us to make changes to files on the server while operating from a local text editor. 

1. Install Remote VSCode extension to VSCode (https://marketplace.visualstudio.com/items?itemName=rafaelmaiolla.remote-vscode)

2. Add the following configuration to VSCode user settings:
```
//-------- Remote VSCode configuration --------

// Port number to use for connection.
"remote.port": 52698,

// Launch the server on start up.
"remote.onstartup": true

// Address to listen on.
"remote.host": "127.0.0.1"

// If set to true, error for remote.port already in use won't be shown anymore.
"remote.dontShowPortAlreadyInUseError": false
```

3. Ssh to remote machine with a ssh tunnel:
```
ssh -R 52698:127.0.0.1:52698 user@example.org
```

4. On the remote machine:
    a. Install rmate: 
    ```gem install rmate```
    b. launch any file for editing like this and it will launch in local editor:
    ```
    rmate -p 52698 file
    ```



