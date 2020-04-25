import time
from flask_slack import Flack, async_task, reply
from slack import WebClient

app = Flack(__name__)
cli = WebClient('xoxb-SECRET-token')


@app.command()
def hello():
    my_background_job()
    return reply('Instant Response')


@async_task
def my_background_job():
    """Non blocking long task"""
    time.sleep(5)  # Wait more than slack's 3 seconds time limit
    cli.chat_postMessage(channel='#general', text='I come from the future')
    return
