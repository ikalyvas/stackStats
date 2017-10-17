## Installation

You need to run the following commands in order to install the package
1. tar xvf encode-python-assignment.tar
2. cd stackStats
3. If you want to use virtualevn (suggested but not necessary.Its good not to pollute the global python libs location)
 * sudo pip install virtualenv
 * virtualenv stats_venv
 * source stats_venv/bin/activate
 * python setup.py install
4. If you dont want to create a virtual environment then you just run the
 * sudo python setup.py install

## How to run the application

 * stats --since "2016-06-2 10:00:00" --until "2016-06-2 11:00:00" --output-format json/html/tab

## How to run the tests

 * cd stackStats
 * python setup.py test
 