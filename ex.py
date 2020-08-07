import urllib
import cv2
import numpy as np
import requests
image_url="https://firebasestorage.googleapis.com/v0/b/face-detector-285211.appspot.com/o/user1%2F1596636890?alt=media"
print(image_url.encode("utf-8"))
def url_to_img(url):
    resp=urllib.request.urlopen(url)
    image=np.asarray(bytearray(resp.read()),dtype=np.uint8)
    print(image.shape)
    image=cv2.imencode(image,cv2.IMREAD_COLOR)

    return image

# print(url_to_img("https://firebasestorage.googleapis.com/v0/b/face-detector-285211.appspot.com/o/user1%2F1596636890?alt=media"))
# r = requests.get(image_url, stream = True)
# print(r.raw)
# import cv2
# import urllib
# import numpy as np

# req = urllib.request.urlopen(image_url)
# arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
# img = cv2.imdecode(arr, -1) # 'Load it as it is'

from cryptography.fernet import Fernet

key = Fernet.generate_key()
with open("secret.key", "wb") as key_file:
    key_file.write(key)