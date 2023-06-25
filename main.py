import openai
import os
import re

from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app_token = os.getenv("SLACK_XAPP").strip()
bot_token = os.getenv("SLACK_XOXB").strip()

# consts
LOADING_STATE = "loading..."

pat = re.compile(r'\Ax[1-9][0-9]*')
app = App(token=bot_token)


def create_response(prompt: str):
    blocks = []
    count = 1
    multiplier = prompt.split(" ")[0]
    if pat.match(multiplier):
        value = int(multiplier[1:])
        if 0 < value < 11:
            count = value
    images = generate_image(prompt, count)
    for image_url in images:
        blocks.append(
            {
                "type": "image",
                "title": {
                    "type": "plain_text",
                    "text": prompt,
                    "emoji": True
                },
                "image_url": image_url,
                "alt_text": prompt,
            }
        )
    return blocks


@app.command("/imagine")
def custom_command_function(ack, respond, command):
    ack()
    respond(response_type="ephemeral", text="loading...")
    if command["text"] == "":
        respond(response_type="ephemeral", text="please specify a prompt and try again.", replace_original=True)
        return
    response_blocks = create_response(command["text"])
    respond(response_type="in_channel", blocks=response_blocks, unfurl_media=True, unfurl_links=True,
            delete_original=True)


def generate_image(prompt: str, quantity: int):
    image_resp = openai.Image.create(prompt=prompt, n=quantity, size="512x512")
    image_urls = []
    for data in image_resp["data"]:
        image_urls.append(data["url"])
    print(image_resp)
    return image_urls


def main():
    openai.organization = os.getenv("OPENAI_ORG").strip()
    openai.api_key = os.getenv("OPENAI_KEY").strip()
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == '__main__':
    main()
