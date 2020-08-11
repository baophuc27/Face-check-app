import cv2
import numpy as np
import requests
import os
basepath='./VN-celeb'
entries = os.listdir("./VN-celeb")
for entry in entries:
     path=os.path.join(basepath, entry)
    
images =  os.listdir(path)
for image_path in images:
    print(os.path.join(path,image_path))
    image=cv2.imread(os.path.join(path,image_path))
    cv2.imshow("image",image)
    cv2.waitKey(0)
# image = cv2.imread("./VN-celeb/483/1.png")
# cv2.imshow("image",image)
# cv2.waitKey(0)
