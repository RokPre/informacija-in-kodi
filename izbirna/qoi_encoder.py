# Read the image.
# Get the width and height of the image.
# The pixel values from the iamge.

import cv2
import sys
import os

image_name = sys.argv[1]

# Check if file is valid
if not os.path.isfile(image_name):
    raise OSError("File is not valid or does not exist.")

image = cv2.imread(image_name)

height = image.shape[0]
width = image.shape[1]

output_bytes: bytearray = bytearray()
prev_pixel: list[int] = [0, 0, 0]
running_list = [[0, 0, 0] for _ in range(64)]
last_index = -1

# Header
output_bytes.extend("qoif".encode("ascii"))
output_bytes.extend(width.to_bytes(length=4, byteorder="big"))  # Width
output_bytes.extend(height.to_bytes(length=4, byteorder="big"))  # Width
output_bytes.append(0b00000011)  # Chanels
output_bytes.append(0b00000001)  # Colorspace

# Data
for h in range(height):
    for w in range(width):
        pixel = image[h][w][::-1]
        pixel = [int(color) for color in pixel]

        color_hash = (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7) % 64

        if pixel == running_list[color_hash] and pixel != prev_pixel:
            output_bytes.append(color_hash)
            prev_pixel = pixel.copy()
            running_list[color_hash] = pixel
            continue

        # If colors are similar only store the differences
        # Check the first 6 bits fo the current pixels color chanels and the previous pixels color chanels
        dr = pixel[0] - prev_pixel[0]
        dg = pixel[1] - prev_pixel[1]
        db = pixel[2] - prev_pixel[2]
        if -2 <= dr <= 1 and -2 <= dg <= 1 and -2 <= db <= 1:
            output_bytes.append(0b01000000 | ((dr + 2) << 4) | ((dg + 2) << 2) | (db + 2))
            prev_pixel = pixel.copy()
            running_list[color_hash] = pixel
            continue

        output_bytes.extend([int(0b11111110), pixel[0], pixel[1], pixel[2]])

        # Update the running_.ist with the current pixel
        running_list[color_hash] = pixel
        prev_pixel = pixel.copy()

# Ending mark
output_bytes.extend(b"\x00\x00\x00\x00\x00\x00\x00\x01")

with open(image_name.replace("png", "qoi"), "wb") as f:
    f.write(output_bytes)
