from PIL import Image

def get_hue(image):
    new_image = image.convert("HSV")
    hue = 0
    samples = 0

    for x in range(0, new_image.size[0]):
        for y in range(0, new_image.size[1]):
            hue  += new_image.getpixel((x, y))[0]

    hue = int(hue/((new_image.size[0]*new_image.size[1])))
    return hue



def get_image_value(image):
    new_image = image.convert("HSV")
    value = 0
    step = 8

    for x in range(0, new_image.size[0],step):
        for y in range(0, new_image.size[1],step):
            value += new_image.getpixel((x,y))[2]

    value = int(value/((new_image.size[0]*new_image.size[1]/step)))
    return value