from PIL import Image

width, height = 256, 256

img = Image.new("RGB", (width, height))
pixels = img.load()


for y in range(height):
    r, g, b = 0, 0, 0
    for x in range(width):
        if x % 3 == 0:
            r = r + 2
        elif x % 2 == 0:
            g = g + 2
        else:
            b = b + 2
        pixels[x, y] = (r, g, b)

img.save("uniq.png")
