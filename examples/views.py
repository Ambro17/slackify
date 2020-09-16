from flask import Flask
from slackify import Slackify, request, text_block, Slack, ACK
import json

from slackify.tasks import async_task

# Important! Before running set FLASK_APP=examples.async_task:app
app = Flask(__name__)
slackify = Slackify(app = app)
cli = Slack('xoxb-SECRET-TOKEN')


@slackify.command
def register():
	username_input_block = {
		"type": "input",
		"block_id": "username_block",
		"element": {
			"type": "plain_text_input",
			"placeholder": {
				"type": "plain_text",
				"text": "Enter your username"
				},
			"action_id": "username_value"
			},
		"label": {
			"type": "plain_text",
			"text": "👤 Username",
			"emoji": True
			}
		}
	password_input_block = {
		"type": "input",
		"block_id": "password_block",
		"element": {
			"type": "plain_text_input",
			"placeholder": {
				"type": "plain_text",
				"text": "Enter your password"
				},
			"action_id": "password_value"
			},
		"label": {
			"type": "plain_text",
			"text": "🔑 Password",
			"emoji": True
			}
		}
	modal_blocks = [
		username_input_block,
		password_input_block,
		]
	registration_form = {
		"type": "modal",
		"callback_id": "registration_form",
		"title": {
			"type": "plain_text",
			"text": "My First Modal",
			"emoji": True
			},
		"submit": {
			"type": "plain_text",
			"text": "Register",
			"emoji": True
			},
		"close": {
			"type": "plain_text",
			"text": "Cancel",
			"emoji": True
			},
		"blocks": modal_blocks
		}
	cli.views_open(
		trigger_id = request.form['trigger_id'],
		view = registration_form
		)
	return ACK


@slackify.view("registration_form")
def register_callback():
	action = json.loads(request.form["payload"])
	response = action['view']['state']['values']
	text_blok = text_block(f':heavy_check_mark: You are now registered.\nPayload:\n```{response}```')
	send_message(cli, [text_blok], action['user']['id'])
	return ACK


@async_task
def send_message(cli, blocks, user_id):
	return cli.chat_postMessage(channel = user_id, user_id = user_id, blocks = blocks)
