import os
from flask import Flask
from slackify import Slackify, request, reply_text, Slack, ACK

# Initialize App
app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack(os.getenv('SLACK_BOT_TOKEN'))


@slackify.command
def update_home_view():
    user = request.form['user_id']
    sample = {
        "type": "home",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "A simple stack of blocks for the simple sample Block Kit Home tab."
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "action_id": "tell_joke",
                        "text": {
                            "type": "plain_text",
                            "text": "Tell me a Joke",
                            "emoji": True
                        }
                    },
                ]
            }
        ]
    }
    resp = cli.views_publish(
        user_id=user,
        view=sample
    )
    assert resp.get('ok', False), f"Could not build home tab.\nError:\n{resp.data!r}"
    return reply_text('Home tab updated.')


@slackify.action('tell_joke')
def tell_a_joke(action):
    resp = cli.chat_postMessage(
        channel=action['user']['id'],  # Send the user a private message through slackbot
        text="I can't remember any joke right now 😅"
    )
    assert resp.get('ok'), f"Error sending message. {resp.data}"
    return ACK


if __name__ == '__main__':
    app.run('0.0.0.0', port=3000)
