import cv2
from PIL import Image 
import pytesseract

im_file = "temp_img.jpg"
im = Image.open(im_file)

# prints mode and size of image
# print(im)

# shows the image / opens up the image
# im.show()

# rotates the image to 90 deg
# im.rotate(90).show()

# saves the image
# im.save("rotated_img.jpg")

# save the rotated image
# im.rotate(90).save("rotated_img.jpg")