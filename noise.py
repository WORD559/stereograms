##Random noise generator

import random
from PIL import Image

def generate(size,mode="RGB"):
    i = Image.new(mode,size)
    pix = i.load()
    for y in range(i.size[1]):
        for x in range(i.size[0]):
            shade = random.randrange(0,256)
            pix[x,y] = (shade,)*3
    return i
            
