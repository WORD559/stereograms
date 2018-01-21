## Autostereogram Generator

from PIL import Image, ImageDraw
import noise
import random

class stereogram(object):
    mu = (1/3.)
    
    def __init__(self,depth_map,pattern=None,DPI=75,verbose=True):
        self.DPI = DPI
        self.eye_separation = int(round(2.5*DPI,0))
        #self.eye_separation = 2.5*DPI
        self.verbose = bool(verbose)
        if pattern != None:
            if isinstance(pattern,str):
                self.pattern = Image.open(pattern)
            elif isinstance(pattern,Image.Image):
                self.pattern = pattern
            else:
                raise TypeError("pattern must be a file path, Image, or None")
        else:
            self.pattern = None

        if isinstance(depth_map,str):
            self.depth_map = Image.open(depth_map)
            self.depth_map = self.depth_map.convert("L")
        elif isinstance(depth_map,Image.Image):
            self.depth_map = depth_map.convert("L")
        else:
            raise TypeError("depth_map must be a file path or an Image")

##        if self.depth_map.size[1] != self.pattern.size[1]:
##            raise ValueError("The height of the pattern and the depth map must match.")

    def __log(self,content):
        if self.verbose:
            print content

    def calculate_stereo_separation(self,z,**kwargs):
        if kwargs.has_key("E"):
            E = kwargs["E"]
        else:
            E = self.eye_separation
        mu = self.mu
        s = int(round((1-mu*z)*E/(2-mu*z),0))
        return s

    def get_pattern_colour(self,x,y,**kwargs):
        if kwargs.has_key("pattern"):
            pattern = kwargs["pattern"]
        else:
            pattern = self.pattern
        pix = pattern.load()
        while x >= pattern.size[0]:
            x -= pattern.size[0]
        while y >= pattern.size[1]:
            y -= pattern.size[1]
        #print x,y
        return pix[x,y]

    def get_random_colour(self):
        shade = random.randrange(0,256)
        return (shade,)*3

    def increase_image_size(self,image,factor):
        return image.resize((int(round(image.size[0]*factor,0)),int(round(image.size[1]*factor,0))),Image.NEAREST)

    def reduce_image_size(self,image,factor):
        return image.resize((int(round(image.size[0]/factor,0)),int(round(image.size[1]/factor,0))),Image.ANTIALIAS)

    def generate(self,AA=1):
        mu = self.mu
        DPI = self.DPI * AA
        E = int(round(2.5*DPI,0))
        
        depth_map = self.increase_image_size(self.depth_map,AA)
        depth = depth_map.load()
        self.stereogram = Image.new("RGB",(depth_map.size[0],depth_map.size[1]))
        for y in range(depth_map.size[1]):
            same = [x for x in range(depth_map.size[0])]
            for x in range(depth_map.size[0]):
                z = depth[x,y]/255.
                s = self.calculate_stereo_separation(z,E=E)

                left = x-s/2
                right = left+s

                if (0 <= left) and (right < depth_map.size[0]-1):
                    t = 1
                    zt = z + 2*(2 - mu*z)*t/(mu*E)
                    visible = ((depth[x-t,y]/255. < zt) and (depth[x+t,y]/255. < zt))
                    t += 1
                    while visible and (zt < 1):
                        zt = z + 2*(2 - mu*z)*t/(mu*E)
                        visible = ((depth[x-t,y]/255. < zt) and (depth[x+t,y]/255. < zt))
                        t += 1
                        #print visible, zt
                    #print "Cleared hidden!"
                    if visible:
                        l = same[left]
                        while (l != left) and (l != right):
                            if (l < right):
                                left = l
                                l = same[left]
                            else:
                                same[left] = right
                                left = right
                                l = same[left]
                                right = l
                        same[left] = right
            pix = self.stereogram.load()
            if self.pattern != None:
                pattern = self.increase_image_size(self.pattern,AA)
            for x in range(depth_map.size[0]-1,0,-1):
                if same[x] == x:
                    if self.pattern == None:
                        pix[x,y] = self.get_random_colour()
                    else:
                        pix[x,y] = self.get_pattern_colour(x,y,pattern=pattern)
                else:
                    pix[x,y] = pix[same[x],y]

        self.stereogram = self.reduce_image_size(self.stereogram,AA)
                    
        draw = ImageDraw.Draw(self.stereogram)
        draw.ellipse((self.depth_map.size[0]/2 - self.calculate_stereo_separation(0)/2 - 10,
                      int(self.depth_map.size[1]*19./20) - 10,
                      self.depth_map.size[0]/2 - self.calculate_stereo_separation(0)/2 + 10,
                      int(self.depth_map.size[1]*19./20) + 10),(0,0,0))
        draw.ellipse((self.depth_map.size[0]/2 + self.calculate_stereo_separation(0)/2 - 10,
                      int(self.depth_map.size[1]*19./20) - 10,
                      self.depth_map.size[0]/2 + self.calculate_stereo_separation(0)/2 + 10,
                      int(self.depth_map.size[1]*19./20) + 10),(0,0,0))
