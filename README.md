Social network Yatube
=================================


Social network Yatube for publishing personal diaries.
A new user can register on this network, create his page, public his notes and photos, subscribe  to another user and comment on his notes or unsubscribe from a user.
Tools: Python3, Django Framework, Django ORM, HTML, Django Templates, Generic Views, Django
Unittest, Pillow library, Cache in dj.

(additinal model Follow and Comment)

Getting Started
===============

1.  You can build it in steps:
    1.  ``cd ...wherever...``
    2.  ``git clone https://github.com/volhadounar/hw05_final``
    3.  ``cd hw05_final``
    4.  ``pip install -r requirements.txt``  -- Should install everything you need
    5.  ``python3 manage.py migrate`` -- Reads all the migrations folders in the application folders and creates / evolves the tables in the database
    6.  ``python3 manage.py runserver`` -- Running localy
    7.  And visit http://127.0.0.1:8000
