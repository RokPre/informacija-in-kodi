import random
from PIL import Image


random_colors = 64 * [0, 0, 0]

for i in range(64):
    r_random = random.randint(0, 255)
    g_random = random.randint(0, 255)
    b_random = random.randint(0, 255)
    random_colors[i] = (r_random, g_random, b_random)


width, height = 256, 256

img = Image.new("RGB", (width, height))
pixels = img.load()


for y in range(height):
    for x in range(width):
        pixels[x, y] = random.choice(random_colors)

img.save("indx.png")
