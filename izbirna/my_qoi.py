import cv2

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


def encode(img):
    """
    Arguments: File path to an image that is not in the QOI format and can be read by cv2.
    Output: Image object:
                height: the height of the image,
                width: the width of the image,
                chanels: "RGB" or "RGBA",
                colorspace: "sRGB" or "linear",
                data: the pixel data [b, g, r] or [b, g, r, a],
                binary: the binary data for the QOI format.
    """
    image = cv2.imread(img, cv2.IMREAD_UNCHANGED)

    if len(image.shape) == 2:
        raise ValueError("QOI format does not support B/W images")

    if image.shape[2] == 2:
        raise ValueError("QOI format does not support grayscale images")

    h = image.shape[0]
    w = image.shape[1]
    is_RGBA = image.shape[2] == 4

    output_bytes: bytearray = bytearray()

    # Header
    output_bytes.extend("qoif".encode("ascii"))  # File signature
    output_bytes.extend(w.to_bytes(length=4, byteorder="big"))  # Width
    output_bytes.extend(h.to_bytes(length=4, byteorder="big"))  # Height

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
        data = encode_RGBA(image, h, w)
    else:
        data = encode_RGB(image, h, w)

    output_bytes.extend(data)

    # Ending mark
    output_bytes.extend(b"\x00\x00\x00\x00\x00\x00\x00\x01")

    class QOIImage:
        height = h
        width = w
        chanels = "RGBA" if is_RGBA else "RGB"
        colorspace = "sRGB" if is_SRGB else "linear"
        data = image
        binary = output_bytes

    return QOIImage


def decode_RGB(data, height, width):
    output_list = [[[0, 0, 0] for _ in range(width)] for _ in range(height)]
    prev_pixel: list[int] = [0, 0, 0]
    running_list: list[list[int]] = [[0, 0, 0] for _ in range(64)]

    byte_index = 0
    run_length = 0
    for h in range(height):
        for w in range(width):
            # pixel = [blue, green, red]

            # Run
            if run_length > 0:
                run_length -= 1
                pixel = prev_pixel.copy()
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                continue

            # Unique
            if data[byte_index] == 0b11111110:
                pixel = [data[byte_index + i] for i in range(3, 0, -1)]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index = byte_index + 4
                continue

            tag = data[byte_index] & 0b11000000
            # Index
            if tag == 0b00000000:
                pixel = running_list[data[byte_index] & 0b00111111]
                output_list[h][w] = pixel.copy()

                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # Diff
            if tag == 0b01000000:
                # pixel = [prev_pixel[i] + ((data[byte_index] >> (2 * i)) & 0b11) - 2 for i in range(0, 3)]
                r = prev_pixel[2] + ((data[byte_index] >> 4) & 0b11) - 2
                g = prev_pixel[1] + ((data[byte_index] >> 2) & 0b11) - 2
                b = prev_pixel[0] + ((data[byte_index] >> 0) & 0b11) - 2
                pixel = [b, g, r]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # Luma
            if tag == 0b10000000:
                dg = (data[byte_index] & 0b00111111) - 32

                byte_index += 1

                drdg = ((data[byte_index] >> 4) & 0b00001111) - 8
                dbdg = ((data[byte_index] >> 0) & 0b00001111) - 8
                dr = drdg + dg
                db = dbdg + dg

                pixel = [(prev_pixel[0] + db) & 0xFF, (prev_pixel[1] + dg) & 0xFF, (prev_pixel[2] + dr) & 0xFF]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # RUN start
            if tag == 0b11000000:
                run_length = data[byte_index] & 0b00111111
                pixel = prev_pixel.copy()
                output_list[h][w] = pixel

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + 255 * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

    return output_list


def decode_RGBA(data, height, width):
    output_list = [[[0, 0, 0, 0] for _ in range(width)] for _ in range(height)]
    prev_pixel: list[int] = [0, 0, 0, 255]
    running_list: list[list[int]] = [[0, 0, 0, 0] for _ in range(64)]

    byte_index = 0
    run_length = 0
    for h in range(height):
        for w in range(width):
            # pixel = [blue, green, red]

            # Run
            if run_length > 0:
                run_length -= 1
                pixel = prev_pixel.copy()
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                continue

            # Unique
            if data[byte_index] == 0b11111111:
                r = data[byte_index + 1]
                g = data[byte_index + 2]
                b = data[byte_index + 3]
                a = data[byte_index + 4]
                pixel = [b, g, r, a]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index = byte_index + 5
                continue

            tag = data[byte_index] & 0b11000000
            # Index
            if tag == 0b00000000:
                pixel = running_list[data[byte_index] & 0b00111111]
                output_list[h][w] = pixel.copy()

                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # Diff
            if tag == 0b01000000:
                # pixel = [prev_pixel[i] + ((data[byte_index] >> (2 * i)) & 0b11) - 2 for i in range(0, 3)]
                r = prev_pixel[2] + ((data[byte_index] >> 4) & 0b11) - 2
                g = prev_pixel[1] + ((data[byte_index] >> 2) & 0b11) - 2
                b = prev_pixel[0] + ((data[byte_index] >> 0) & 0b11) - 2
                a = prev_pixel[3]
                pixel = [b, g, r, a]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # Luma
            if tag == 0b10000000:
                dg = (data[byte_index] & 0b00111111) - 32

                byte_index += 1

                drdg = ((data[byte_index] >> 4) & 0b00001111) - 8
                dbdg = ((data[byte_index] >> 0) & 0b00001111) - 8
                dr = drdg + dg
                db = dbdg + dg

                a = prev_pixel[3]

                pixel = [(prev_pixel[0] + db) & 0xFF, (prev_pixel[1] + dg) & 0xFF, (prev_pixel[2] + dr) & 0xFF, a]
                output_list[h][w] = pixel.copy()

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

            # RUN start
            if tag == 0b11000000:
                run_length = data[byte_index] & 0b00111111
                pixel = prev_pixel.copy()
                output_list[h][w] = pixel

                color_hash = (pixel[2] * 3 + pixel[1] * 5 + pixel[0] * 7 + pixel[3] * 11) % 64
                running_list[color_hash] = pixel.copy()
                prev_pixel = pixel.copy()
                byte_index += 1
                continue

    return output_list


def decode(img):
    """
    Arguments: File path to an image that is in the QOI format and can be read by cv2.
    Output: Image object:
                height: the height of the image,
                width: the width of the image,
                chanels: "RGB" or "RGBA",
                colorspace: "sRGB" or "linear",
                data: the pixel data [b, g, r] or [b, g, r, a],
                binary: the binary data for the QOI format.
    """
    with open(img, "rb") as f:
        file = f.read()

        header = file[0:14]
        data = file[14:-8]
        end = file[-8:]

        if header[0:4] != "qoif".encode("ascii"):
            raise ValueError("Not qoif file.")

        if end != b"\x00\x00\x00\x00\x00\x00\x00\x01":
            raise ValueError("Not qoif file.")

        w = int.from_bytes(header[4:8], "big")
        h = int.from_bytes(header[8:12], "big")
        is_RGBA = header[12] == 4
        is_SRGB = header[13] == 0

        if is_RGBA:
            image_data = decode_RGBA(data, h, w)
        else:
            image_data = decode_RGB(data, h, w)

        class QOIImage:
            height = h
            width = w
            chanels = "RGBA" if is_RGBA else "RGB"
            colorspace = "sRGB" if is_SRGB else "linear"
            data = image_data
            binary = file

    return QOIImage
