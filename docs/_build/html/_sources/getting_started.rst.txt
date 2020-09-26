###############
Getting Started
###############

Installation
============
The first step to use slackify is to install it inside your virtualenv

.. code-block:: shell

    python3 -m pip install slackify


.. note:: Slackify requires python3.6 or higher to run


Running the bot
===============
To run the bot create a file named :code:`app.py` with the following content

.. code-block:: python

    from flask import Flask
    from slackify import Slackify, reply_text

    app = Flask(__name__)
    slackify = Slackify(app=app)


    @slackify.command
    def hello():
        return reply_text('Hello from Slackify!')


    if __name__ == '__main__':
        app.run(host='0.0.0.0', port=5000)

Then run the server with

.. code-block:: shell

    python3 app.py

What happened here?
We created a :code:`Flask` app, then we passed it to Slackify to get a 
slackified app.
Then we decorated a function with :code:`@slackify.command` to register it
as the function that should be called when slack user invokes :code:`/hello`

Let's check if it works, type :code:`http://localhost:5000/hello` in your browser.
You should see the following response:

.. code-block:: json

    {
        "text": "Hello from Slackify!"
    }

Great! Now our bot is fully operational, but we must connect it to slack so 
users other than ourselves can start using it. Let's do that


Connecting to slack
===================

Slack requires a publicly available url for our bot,
while developing it might get tedious to upload every change to a public server
just to test if everything works.
To overcome this we can use ngrok to create an https tunnel from a 
public, temporal url, to your localhost server.

That way slack has the url it needs, but we can still quickly make
changes to our bot to change its behaviour.

To connect our bot we must complete these 2 Steps:

1. Install ngrok
2. Create slack app pointing to our ngrok's public url

Install ngrok
-------------

Go to https://ngrok.com/download and follow the instructions
Then run :code:`ngrok http 5000`. This will expose an http url, and redirect
all requests to localhost on port 5000.

Create a Slack App
------------------
Go to https://api.slack.com/apps?new_app=1 and create a new app.
Enable :code:`Bots` feature and install it to your workspace, then 
save your `Bot User OAuth Access Token` that we will need later.
Enable :code:`Slash Commands` feature and create a new command 
:code:`hello` with the url set to ngrok's http url of step #1


.. note:: 
    It might ask you to login to your workspace before creating an app.
    After you login, follow that link and you should be able to create it
