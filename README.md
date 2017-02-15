Manual for Ubuntu.
1) First of all we need to install "pip" and "virtualenv", write in terminal:

sudo apt-get install pip

sudo apt-get install virtualenv

2) Then after installation, to create virtual environment folder write in terminal:

virtualenv Jillerenv

3) Now, to activate environment, go to the new folder (in terminal write "cd Jillerenv") and write:

source bin/activate

4) Now your terminal is using your own virtual environment. Let's install packages for our django project. Download our project from github into Jillerenv folder. To install packages write in terminal:

pip install -r Jiller/requirements.txt 

note: after git your folder can have name "Jiller-master".
 
5) After installation you can check version of your Django by typing
django-admin.py --version

In our environment it should be 1.10.5

6) To make role permissions work:

delete your database

if your migrations ain't up to date: $ python manage.py makemigrations

$ python manage.py migrate

$ python manage.py loaddata project/fixtures/init_data.json

(You get 4 users: admin, developer, scrum_master, product_owner
password for all: test)

to check and run celery for sending async emails:

$ celery -A Jiller worker -l info
