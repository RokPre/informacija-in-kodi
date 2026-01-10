# Download image file.
# Run encoder.
# Check pixel data on original and encoder output.
# Run decoder.
# Check pixel data on original and decoder output.

original_image_folder = "images"
encoded_image_folder = "encoded"
decoded_image_folder = "decoded"

import cv2
import os
import qoi_encoder
import qoi_decoder
import numpy as np
import qoi


def func():
    np.uint8()
    cv2.imread("")
    os.path.join("", "")
    qoi_encoder.encode_RGBA("", "", "")
    qoi_decoder.decode_RGBA("", "", "")


# Get file
original_files = os.listdir(original_image_folder)

for i, image_name in enumerate(original_files):
    image_name = os.path.join(original_image_folder, image_name)
    image = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)

    if image is None:
        continue

    height = image.shape[0]
    width = image.shape[1]

    if len(image.shape) == 2:
        print(f"Black and white images are not yet supported: {image_name}")
        continue

    if image.shape[2] == 2:
        print(f"Grayscale images are not yet supported: {image_name}")
        continue

    is_RGBA = image.shape[2] == 4

    # Init of output array
    output_bytes: bytearray = bytearray()

    # Header
    output_bytes.extend("qoif".encode("ascii"))  # File signature
    output_bytes.extend(width.to_bytes(length=4, byteorder="big"))  # Width
    output_bytes.extend(height.to_bytes(length=4, byteorder="big"))  # Height

    if is_RGBA:
        output_bytes.append(0b00000100)  # Chanels
    else:
        output_bytes.append(0b00000011)  # Chanels

    is_SRGB: bool = False  # Typically false. TODO: Detection
    if is_SRGB:
        output_bytes.append(0b00000000)  # Colorspace
    else:
        output_bytes.append(0b00000001)  # Colorspace

    if is_RGBA:
        data = qoi_encoder.encode_RGBA(image, height, width)
    else:
        data = qoi_encoder.encode_RGB(image, height, width)

    output_bytes.extend(data)

    # Ending mark
    output_bytes.extend(b"\x00\x00\x00\x00\x00\x00\x00\x01")

    file_type = image_name.split(".")[-1]
    image_name, ext = os.path.splitext(image_name)
    image_name = image_name + ".qoi"
    output_file_name = image_name.replace(original_image_folder, encoded_image_folder)
    with open(output_file_name, "wb") as f:
        f.write(output_bytes)

    print(f"File saved in: {output_file_name}")

# ----------------------------------------------
encoded_files = os.listdir(encoded_image_folder)

for i, image_name in enumerate(encoded_files):
    with open(os.path.join(encoded_image_folder, image_name), "rb") as f:
        file = f.read()
        header = file[0:14]
        data = file[14:-8]
        end = file[-8:]

        if header[0:4] != "qoif".encode("ascii"):
            raise ValueError("Not qoif file.")

        if end != b"\x00\x00\x00\x00\x00\x00\x00\x01":
            raise ValueError("Not qoif file.")

        width = int.from_bytes(header[4:8], "big")
        height = int.from_bytes(header[8:12], "big")
        is_RGBA = header[12] == 4
        is_SGBA = header[13] == 0

        if is_RGBA:
            image_data = qoi_decoder.decode_RGBA(data, height, width)
        else:
            image_data = qoi_decoder.decode_RGB(data, height, width)

    if image_data is None:
        continue
    image_data = np.array(image_data)

    image_name, ext = os.path.splitext(image_name)
    image_name = image_name + ".png"
    output_file_name = os.path.join(decoded_image_folder, image_name)
    cv2.imwrite(output_file_name, np.array(image_data))

    print("Image save to:", output_file_name)


# ----------------------------------------------
for image_index, image_name in enumerate(original_files):
    print(f"Checking on file: {image_name}")
    original_path = os.path.join(original_image_folder, image_name)
    e_image_name, ext = os.path.splitext(image_name)
    e_image_name = e_image_name + ".qoi"
    encoded_path = os.path.join(encoded_image_folder, e_image_name)
    decoded_path = os.path.join(decoded_image_folder, image_name)

    # print(original_path)
    # print(encoded_path)
    # print(decoded_path)
    original = cv2.imread(original_path, cv2.IMREAD_UNCHANGED)
    decoded = cv2.imread(decoded_path, cv2.IMREAD_UNCHANGED)
    with open(encoded_path, "rb") as f:
        encoded = qoi.decode(f.read())

    # print(type(original))
    # print(type(encoded))
    # print(type(decoded))

    # if original is None or encoded is None or decoded is None:
    #     print(f"Failed to load {image_name}")
    #     continue

    if original is None or decoded is None:
        print(f"Failed to load {image_name}")
        continue

    # if original.shape != encoded.shape or original.shape != decoded.shape:
    #     print(f"Shape mismatch in {image_name}")
    #     continue

    if original.shape != decoded.shape:
        print(f"Shape mismatch in {image_name}")
        continue

    height, width = original.shape[:2]

    for y in range(height):
        for x in range(width):
            op = original[y, x]  # Blue, Green, Red
            ep = encoded[y][x]  # Red, Green, Blue
            dp = decoded[y, x]  # Blue, Green, Red

            if len(ep) == 4:
                ep = [ep[2], ep[1], ep[0], ep[3]]
            elif len(ep) == 3:
                ep = [ep[2], ep[1], ep[0]]

            if not np.array_equal(op, ep):
                print(f"{image_name}: original != encoded at ({y}, {x})")
                print(op)
                print(ep)
                print(dp)
                break

            if not np.array_equal(op, dp):
                print(f"{image_name}: original != decoded at ({y}, {x})")
                print(op)
                print(ep)
                print(dp)
                break

            if not np.array_equal(ep, dp):
                print(f"{image_name}: encoded != decoded at ({y}, {x})")
                print(op)
                print(ep)
                print(dp)
                break
    f.close()
