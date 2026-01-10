import cv2
import sys
import os

SUPPORTED_FILE_TYPES = ["png"]


def encode_RGBA(image, height, width):
    output_bytes = bytearray()
    prev_pixel: list[int] = [0, 0, 0, 255]
    running_list = [[0, 0, 0, 0] for _ in range(64)]
    run = 0
    color_hash = 0
    for h in range(height):
        for w in range(width):
            # Get the new pixel
            pixel = image[h][w]  # pixel = [Blue, Green, Red, Alpha]
            pixel = [int(chanel) for chanel in pixel]  # Convert to int from np.uint8

            # Run
            if pixel == prev_pixel and run < 62:
                run += 1
                continue

            if run > 0:
                output_bytes.append(0b11000000 | (run - 1))
                run = 0

            color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64

            # Index
            if pixel == running_list[color_hash] and pixel != prev_pixel:
                output_bytes.append(color_hash)

                prev_pixel = running_list[color_hash]
                continue

            # Diff
            diff = [pixel[i] - prev_pixel[i] for i in range(len(pixel))]
            if -2 <= diff[0] <= 1 and -2 <= diff[1] <= 1 and -2 <= diff[2] <= 1 and diff[3] == 0 and pixel != prev_pixel:
                output_bytes.append(0b01000000 | ((diff[2] + 2) << 4) | ((diff[1] + 2) << 2) | (diff[0] + 2))

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                continue

            # Luma
            difg = diff[1]  # Green. pixel = [Blue, Green, Red] => diff = [Blue_diff, Green_diff, Red_diff]
            drdg = diff[2] - diff[1]  # dr - dg = pixel[2] - prev_pixel[2] - (pixel[1] - prev_pixel[1])
            dbdg = diff[0] - diff[1]  # db - dg = pixel[0] - prev_pixel[0] - (pixel[1] - prev_pixel[1])
            if -32 <= difg <= 31 and -8 <= drdg <= 7 and -8 <= dbdg <= 7 and diff[3] == 0 and pixel != prev_pixel:
                output_bytes.extend([0b10000000 | (difg + 32), (drdg + 8) << 4 | (dbdg + 8)])

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                continue

            output_bytes.extend([int(0b11111111), pixel[2], pixel[1], pixel[0], pixel[3]])
            running_list[color_hash] = pixel.copy()
            prev_pixel = pixel.copy()

    # Run flush
    if run > 0:
        output_bytes.append(0b11000000 | (run - 1))

    return output_bytes


def encode_RGB(image, height, width):
    output_bytes = bytearray()
    prev_pixel: list[int] = [0, 0, 0]
    running_list = [[0, 0, 0] for _ in range(64)]
    run = 0
    color_hash = 0
    for h in range(height):
        for w in range(width):
            # Get the new pixel
            pixel = image[h][w]  # pixel = [Blue, Green, Red]
            pixel = [int(chanel) for chanel in pixel]  # Convert to int from np.uint8

            # Run
            if pixel == prev_pixel and run < 62:
                run += 1
                continue

            if run > 0:
                output_bytes.append(0b11000000 | (run - 1))
                run = 0

            color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64

            # Index
            if pixel == running_list[color_hash] and pixel != prev_pixel:
                output_bytes.append(color_hash)

                prev_pixel = running_list[color_hash]
                continue

            # Diff
            diff = [pixel[i] - prev_pixel[i] for i in range(len(pixel))]
            if -2 <= diff[0] <= 1 and -2 <= diff[1] <= 1 and -2 <= diff[2] <= 1 and pixel != prev_pixel:
                output_bytes.append(0b01000000 | ((diff[2] + 2) << 4) | ((diff[1] + 2) << 2) | (diff[0] + 2))

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                continue

            # Luma
            difg = diff[1]  # Green. pixel = [Blue, Green, Red] => diff = [Blue_diff, Green_diff, Red_diff]
            drdg = diff[2] - diff[1]  # dr - dg = pixel[2] - prev_pixel[2] - (pixel[1] - prev_pixel[1])
            dbdg = diff[0] - diff[1]  # db - dg = pixel[0] - prev_pixel[0] - (pixel[1] - prev_pixel[1])
            if -32 <= difg <= 31 and -8 <= drdg <= 7 and -8 <= dbdg <= 7 and pixel != prev_pixel:
                output_bytes.extend([0b10000000 | (difg + 32), (drdg + 8) << 4 | (dbdg + 8)])

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                continue

            output_bytes.extend([int(0b11111110), pixel[2], pixel[1], pixel[0]])
            running_list[color_hash] = pixel.copy()
            prev_pixel = pixel.copy()

    # Run flush
    if run > 0:
        output_bytes.append(0b11000000 | (run - 1))

    return output_bytes


def main():
    # Check if user inputed a file
    if len(sys.argv) < 2:
        raise ValueError("No input file specified.")

    if len(sys.argv) == 2:
        args = [sys.argv[1]]
    else:
        args = sys.argv[1:]

    for image_name in args:
        # Check if file is valid
        if not os.path.isfile(image_name):
            raise OSError(f"File is not valid or does not exist: {image_name}")

        try:
            file_type = image_name.split(".")[-1]
        except:
            raise ValueError("Unable to determine the file type.")

        if file_type.lower() not in SUPPORTED_FILE_TYPES:
            raise NotImplementedError("File type is not supported:", file_type)

        image = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)

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
            data = encode_RGBA(image, height, width)
        else:
            data = encode_RGB(image, height, width)

        output_bytes.extend(data)

        # Ending mark
        output_bytes.extend(b"\x00\x00\x00\x00\x00\x00\x00\x01")

        output_file_name = image_name.replace(file_type, "qoi")
        with open(output_file_name, "wb") as f:
            f.write(output_bytes)

        print(f"File saved in: {output_file_name}")


if __name__ == "__main__":
    main()
