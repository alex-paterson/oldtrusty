First install pip with `sudo easy_install pip` on OSX or `sudo apt-get install python-pip python-dev build-essential` on Linux.

The install virtualenv with `sudo pip install --upgrade virtualenv`.

Then create a virtual environment in the project directory with `virtualenv venv`.

Then activate it with `source venv/bin/activate`.

Now run `python` to make sure it's python2.7. If it's not, start again, but create the virtualenv env with `virtualenv -p $PYTHON2PATH venv`.

If `python` outside of virtualenv if python2.7, you can run `which python` to get the path.

Then install dependencies with `pip install -r requirements.txt`

Now you can run `python server.py` and `python client.py` without any missing dependencies.

To deactivate the virtualenv run `deactivate`.
