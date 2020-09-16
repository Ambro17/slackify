import os

import Slack as Slack

from slackify import Slackify, Flask, Slack

# Initialize App
app = Flask(__name__)
slackify = Slackify(app = app)
cli = Slack(os.getenv('SLACK_BOT_TOKEN'))


def show_home():
	home_blocks = [{
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
					"text": {
						"type": "plain_text",
						"text": "Action A",
						"emoji": True
						}
					},
				{
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Action B",
						"emoji": True
						}
					}
				]
			}
		]
	return home_blocks


@slackify.event('app_home_opened')
def home_hook(payload):
	event = payload["event"]
	if (event['type'] == 'app_home_opened') and ('tab' in event) and (event['tab'] == 'home'):
		user = event['user']
		channel = event['channel']
		blocks = show_home()
		views = {"type": "home", "blocks": blocks}
		cli.views_publish(user_id = user, view = views)
