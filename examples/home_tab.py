import os

import Slack as Slack

from slackify import Slackify, Flask, Slack

# Initialize App
app = Flask(__name__)
slackify = Slackify(app = app)
cli = Slack(os.getenv('SLACK_BOT_TOKEN'))


@slackify.event("app_home_opened")
def show_home(payload):
	home_blocks = {
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
		}
	cli.views_publish(
		event = payload['event'],
		user_id = event['user']['id'],
		view = home_blocks
		)
	return OK


@slackify.view("home_blocks")
def home_tab_callback():
	action = json.loads(request.form["payload"])
	response = action['view']['state']['values']
	text_blok = text_block(f':heavy_check_mark: You are now registered.\npayload:\n```{response}```')
	views_publish(cli, action['user']['id'], home)
	return ACK


if __name__ == "__main__":
	app.run(port = os.environ.get('PORT'))
