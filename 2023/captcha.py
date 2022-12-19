import requests
from io import BytesIO
import matplotlib.pyplot as plt
from PIL import Image

get_captcha_url = "https://www.yooc.me/group/get_captcha"

json_resp = requests.get(get_captcha_url).json()

img_url = json_resp["img"]

img_resp = requests.get(img_url).content
img_stream = BytesIO(img_resp)

img = Image.open(img_stream)
img.show()