import os
import random
import re

from flask import Flask
from slackify import (
	ACK, OK, Slackify, async_task, block_reply,
	request, respond, text_block, reply_text, Slack)

app = Flask(__name__)
slackify = Slackify(app = app)
cli = Slack(os.getenv('BOT_TOKEN'))


@slackify.command
def hello():
	YES = 'yes'
	NO = 'no'
	yes_no_buttons_block = {
		"type": "actions",
		"elements": [
			{
				"type": "button",
				"text": {
					"type": "plain_text",
					"emoji": True,
					"text": "Yes"
					},
				"style": "primary",
				"value": "i_like_bots",
				"action_id": YES
				},
			{
				"type": "button",
				"text": {
					"type": "plain_text",
					"emoji": True,
					"text": "No"
					},
				"style": "danger",
				"value": "i_dont_like_bots",
				"action_id": NO
				}
			]
		}
	blocks = [
		text_block('Do you like Bots?'),
		yes_no_buttons_block
		]
	return block_reply(blocks)


@slackify.action("yes")
def yes(action):
	text_blok = text_block('Super! I do too :thumbsup:')
	respond(action['response_url'], {'blocks': [text_blok]})
	return OK


@slackify.action("no")
def no(action):
	text_blok = text_block('Boo! You are so boring :thumbsdown:')
	respond(action['response_url'], {'blocks': [text_blok]})
	return OK


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
	callback_id = 'registration_form'
	registration_form = {
		"type": "modal",
		"callback_id": callback_id,
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
	return OK


@slackify.view("registration_form")
def register_callback(payload):
	response = payload['view']['state']['values']
	text_blok = text_block(f':heavy_check_mark: You are now registered.\nForm payload:\n```{response}```')
	send_message(cli, [text_blok], payload['user']['id'])
	return ACK


@async_task
def send_message(cli, blocks, user_id):
	return cli.chat_postMessage(channel = user_id, user_id = user_id, blocks = blocks)


@slackify.shortcut('dice_roll')
def dice_roll(payload):
	dice_value = random.randint(1, 6)
	msg = f'🎲 {dice_value}'
	send_message(cli, blocks = [text_block(msg)], user_id = payload['user']['id'])
	return ACK


@slackify.event('reaction_added')
def echo_reaction(payload):
	event = payload['event']
	reaction = event['reaction']
	cli.reactions_add(
		name = reaction,
		channel = event['item']['channel'],
		timestamp = event['item']['ts']
		)


@slackify.message('hello')
def say_hi(payload):
	event = payload['event']
	cli.chat_postMessage(channel = event['channel'], text = 'Hi! 👋')


@slackify.message(re.compile(r'python', re.IGNORECASE))
def reply_python_emoji(payload):
	event = payload['event']
	cli.reactions_add(
		name = 'snake',
		channel = event['channel'],
		timestamp = event['ts']
		)


@slackify.command
def register():
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
		user_id = user,
		view = sample
		)
	assert resp.get('ok', False), f"Could not build home tab.\nError:\n{resp.data!r}"
	return reply_text(f'You are `{user}`.')


@slackify.action('tell_joke')
def tell_a_joke(action):
	resp = cli.chat_postMessage(
		channel = action['user']['id'],  # Send the user a private message through slackbot
		text = "I can't remember any joke right now 😅"
		)
	assert resp.get('ok'), f"Error sending message. {resp.data}"
	return ACK


if __name__ == '__main__':
	print('Running')
	app.run('0.0.0.0', port = 3000)
