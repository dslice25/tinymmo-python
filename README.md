
Requires python 2.7

Tested on Mac OSX 10+


###Setup using virtual environment:

```
git clone https://github.com/dslice25/tinymmo.git
cd tinymmo-python
virtualenv pyenv
source pyenv/bin/activate
pip install twisted pytmx pyglet pyinstaller pillow
pip install git+https://github.com/jorgecarleitao/pyglet-gui.git
pip install git+https://github.com/padraigkitterick/pyglet-twisted
```


#### Quickstart:

After setting up in a virtual environment you should be able to run the server and client. By default server listens on localhost:10000.

```
source pyenv/bin/activate
python game_server.py
```

Then in a new terminal:

```
source pyenv/bin/activate
python game_client.py
```
 

###Build the client on Mac (for mac):

```
source pyenv/bin/activate
pyinstaller game_client.py --add-data data:data
```

See pyinstaller docs (https://pyinstaller.readthedocs.io/en/stable/index.html) for additional build options.

You can now distribute build/game_client to users.


###Build the client on Windows (for windows):

TODO

###Build the client on Linux (for linux):

TODO
