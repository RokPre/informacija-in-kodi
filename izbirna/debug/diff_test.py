from PIL import Image

width, height = 256, 256

img = Image.new("RGB", (width, height))
pixels = img.load()

for y in range(height):
    for x in range(width):
        r = 0
        g = x
        b = 0
        pixels[x, y] = (r, g, b)

img.save("diff.png")
