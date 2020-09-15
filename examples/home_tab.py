import os

import Slack as Slack

from slackify import Slackify, Flask, Slack

# Initialize App
app = Flask(__name__)
slackify = Slackify(app = app)
cli = Slack(os.getenv('SLACK_BOT_TOKEN'))


@slackify.event('app_home_opened')
def show_home(payload):
	{
		"type": "home",
		"callback_id": "show_home_tab",
		"blocks": [
			{
				"type": "header",
				"text": {
					"type": "plain_text",
					"text": ":newspaper:  Paper Company Newsletter  :newspaper:"
					}
				},
			{
				"type": "context",
				"elements": [
					{
						"text": "*November 12, 2019*  |  Sales Team Announcements",
						"type": "mrkdwn"
						}
					]
				},
			{
				"type": "divider"
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": " :loud_sound: *IN CASE YOU MISSED IT* :loud_sound:"
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Replay our screening of *Threat Level Midnight* and pick up a copy of the DVD to give to your customers at the front desk."
					},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Watch Now",
						"emoji": true
						}
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "The *2019 Dundies* happened. \nAwards were given, heroes were recognized. \nCheck out *#dundies-2019* to see who won awards."
					}
				},
			{
				"type": "divider"
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": ":calendar: |   *UPCOMING EVENTS*  | :calendar: "
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "`11/20-11/22` *Beet the Competition* _ annual retreat at Schrute Farms_"
					},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "RSVP",
						"emoji": true
						}
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "`12/01` *Toby's Going Away Party* at _Benihana_"
					},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Learn More",
						"emoji": true
						}
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "`11/13` :pretzel: *Pretzel Day* :pretzel: at _Scranton Office_"
					},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "RSVP",
						"emoji": true
						}
					}
				},
			{
				"type": "divider"
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": ":calendar: |   *PAST EVENTS*  | :calendar: "
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "`10/21` *Conference Room Meeting*"
					},
				"accessory": {
					"type": "button",
					"text": {
						"type": "plain_text",
						"text": "Watch Recording",
						"emoji": true
						}
					}
				},
			{
				"type": "divider"
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "*FOR YOUR INFORMATION*"
					}
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": ":printer: *Sabre Printers* are no longer catching on fire! The newest version of our printers are safe to use. Make sure to tell your customers today.",
					"verbatim": false
					}
				},
			{
				"type": "divider"
				},
			{
				"type": "section",
				"text": {
					"type": "mrkdwn",
					"text": "Please join me in welcoming our 3 *new hires* to the Paper Company family! \n\n *Robert California*, CEO \n\n *Ryan Howard*, Temp \n\n *Erin Hannon*, Receptionist "
					}
				},
			{
				"type": "divider"
				},
			{
				"type": "context",
				"elements": [
					{
						"type": "mrkdwn",
						"text": ":pushpin: Do you have something to include in the newsletter? Here's *how to submit content*."
						}
					]
				}
			]
		}
	cli.views_publish(
		trigger_id = request.form['trigger_id'],
		view = show_home_tab
		)
	return ACK

@slackify.view("show_home_tab")
def home_tab_callback():
	action = json.loads(request.form["payload"])
	response = action['view']['state']['values']
	return ACK


if __name__ == "__main__":
	app.run(port = os.environ.get('PORT'))
