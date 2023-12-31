import os
import re

import openai
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

app_token = os.getenv("SLACK_XAPP").strip()
bot_token = os.getenv("SLACK_XOXB").strip()

# consts
LOADING_STATE = "loading..."
MULTIPLIER_PATTERN = re.compile(r'\Ax[1-9][0-9]*')

# app
app = App(token=bot_token)


def create_response(prompt: str):
    blocks = []
    count = 1
    prompt_list = prompt.split(" ")[0]
    multiplier = prompt_list[0]
    if MULTIPLIER_PATTERN.match(multiplier):
        value = int(multiplier[1:])
        if 0 < value < 11:
            count = value
        prompt = "".join(prompt_list[1:])
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
def imagine_command(ack, respond, command):
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
    # verify env variables have been loaded correctly
    if openai.organization == "" or openai.api_key == "" or app_token == "" or bot_token == "":
        raise Exception("one or more environment variables could not be loaded")
    # create socket handler and start accepting connections
    handler = SocketModeHandler(app, app_token)
    handler.start()


if __name__ == '__main__':
    main()
