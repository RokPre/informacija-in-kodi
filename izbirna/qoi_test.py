import my_qoi
import os
import cv2

images_folder = "images"
files = os.listdir(images_folder)

for file in files:
    org_img_path = os.path.join(images_folder, file)
    encoded_path = os.path.join("encoded", file)

    org_img = cv2.imread(org_img_path, cv2.IMREAD_UNCHANGED)

    encoded = my_qoi.encode(org_img_path)

    with open(encoded_path, "wb") as f:
        f.write(encoded.binary)

    decoded = my_qoi.decode(encoded_path)

    for w in range(decoded.width):
        for h in range(decoded.height):
            for c in range(len(decoded.data[h][w])):
                if org_img[h][w][c] != decoded.data[h][w][c]:
                    raise ValueError("Pixel data does not match")

    print(f"{org_img_path} matches {encoded_path}")
