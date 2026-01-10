# python3 qoi_decoder.py <input_file> <output_file>
# python3 qoi_decoder.py <input_file1> <input_file2> ...

import sys
import cv2
import numpy as np


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


def main():
    # Chek the user input.
    if len(sys.argv) < 2:
        # No file was given
        raise ValueError("No input file specified.")

    elif len(sys.argv) < 3:
        # Only the input file was given.
        raise ValueError("Please provide input and ouput files.")

    elif len(sys.argv) == 3:
        # Input and output file were given.
        input_files = [sys.argv[1]]
        output_files = [sys.argv[2]]

    else:
        # Multiple input files were given.
        input_files = sys.argv[1:]
        output_files = [str(output_file).replace("qoi", "png") for output_file in sys.argv[1:]]

    for i, input_file in enumerate(input_files):
        with open(input_file, "rb") as f:
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
                image_data = decode_RGBA(data, height, width)
            else:
                image_data = decode_RGB(data, height, width)

        if image_data is None:
            continue
        image_data = np.array(image_data)

        cv2.imwrite(output_files[i], np.array(image_data))


if __name__ == "__main__":
    main()
