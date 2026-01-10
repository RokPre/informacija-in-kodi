from PIL import Image

width, height = 1, 1

img = Image.new("RGB", (width, height))
pixels = img.load()

pixels[0, 0] = (255, 0, 0)
img.save("oner.png")

pixels[0, 0] = (0, 255, 0)
img.save("oneg.png")

pixels[0, 0] = (0, 0, 255)
img.save("oneb.png")
