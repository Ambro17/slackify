import os
from slackify import Slackify, Flask, Slack

# Initialize App
app = Flask(__name__)
slackify = Slackify(app=app)
cli = Slack(os.getenv('SLACK_BOT_TOKEN'))


# Create greeting with formatted text response
@slackify.message('hello')
def say_hi(payload):
    event = payload['event']
    cli.chat_postMessage(
        channel=event['channel'],
        # Blocks can be used to insert markdown support for links, images, and more.
        # Check out https://api.slack.com/reference/block-kit for more.
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Danny Torrence left the following review for your property:"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "<https://example.com|Overlook Hotel> \n :star:\n" + \
                            "Doors had too many axe holes, guest in room " + \
                            "237 was far too rowdy, whole place felt stuck in the 1920s."
                },
                "accessory": {
                    "type": "image",
                    "image_url": "https://images.pexels.com/photos/750319/pexels-photo-750319.jpeg",
                    "alt_text": "Haunted hotel image"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Average Rating*\n1.0"
                    }
                ]
            }
        ]
    )
