import getopt
import sys
from sys import argv

import openai
import requests
import os


def generate_image(prompt: str):
    image_resp = openai.Image.create(prompt=prompt, n=4, size="512x512")
    for idx, data in enumerate(image_resp["data"]):
        folder_path = "output"  # Replace with the desired folder path
        # Extract the filename from the URL
        filename = "{}_{}.png".format("".join(c if c.isalnum() else "_" for c in prompt)[:40], idx)
        # Make a GET request to the URL
        response = requests.get(data["url"])
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Save the image to the folder
            file_path = os.path.join(folder_path, filename)
            with open(file_path, "wb") as file:
                file.write(response.content)
            print("Image downloaded and saved successfully.")
        else:
            print("Failed to download the image.")
    print(image_resp)


def main():
    openai.organization = os.getenv("OPENAI_ORG")
    openai.api_key = os.getenv("OPENAI_KEY")
    if openai.organization is None or openai.api_key is None:
        print("missing required environment variables")

    try:
        _, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    if len(args) < 2:
        print("not enough args")
    else:
        generate_image(args[1])


main()
