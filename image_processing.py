# this file is called from main
# it does the image processing, mainly generating the sequences of frames for the sprites

from PIL import Image
import os

# ratio for scaling the ship images in the end
ratio = 1/3

# 1.0 create ships frames #####################################################

# define function that shears image and shifts it back s.t. the fulcrum of the oars stays in place

def add_border(img, shift_factor, symmetry_axis):
    new = Image.new('RGB', (img.width, int(img.height)), (0, 0, 0))
    new.putalpha(0)
    new.paste(img, (0, int(1.1 * img.width - img.height/2 + (img.width * symmetry_axis) * shift_factor)), img)
    return new

def shear(img, shear):
    shear = img.transform(img.size, Image.AFFINE, (1, 0, 0, shear, 1, 0))
    return shear

def tips_in_water(img, cut, side, alpha = 0.3):
    #img0 is the original image
    img0 = img.copy()
    
    # img1 is empty
    img1 = img.copy()
    img1.putalpha(0)
    
    # fill right half of img 1 with img 0 
    if side == "left":
        rect = (int(img.width * cut),0,img.width,img.height)
        img1.paste(img0.crop(rect), (int(img0.width * cut), 0), img0.crop(rect))
    
    if side == "right":
        rect = (0,0,img.width - int(img.width * cut),img.height)
        img1.paste(img0.crop(rect), (0, 0), img0.crop(rect))

    # img2 is the blend of image 0 and 1
    img2 = Image.blend(img0, img1, alpha = alpha)

    return img2

# generate frames for each ship type

for j in range(0,4):
    # load basic images
    
    rumpf = Image.open("images/rumpf_" + str(j) +  ".png") 
    rumpfcopy = rumpf.copy()
    
    ruder_links = Image.open("images/ruder_links_" + str(j) + ".png")
    ruder_links_copy = ruder_links.copy()
    
    #create one image per frame for the rowing sequence and save result
    
    frames_per_direction = 20
    for i in range(0,frames_per_direction):
    
        shear_factor = i/frames_per_direction
        
        ruder_links_copy = ruder_links.copy()
        
    #shear images of oars 
        ruder_links_copy = add_border(ruder_links, shear_factor, 1/3)
        ruder_links_copy = shear(ruder_links_copy, shear_factor)
        
        ruder_rechts_copy = ruder_links_copy.transpose(Image.FLIP_LEFT_RIGHT)

    # generate extra images for second and third row of oars
        ruder_links_copy1 = ruder_links_copy.copy()
        ruder_links_copy2 = ruder_links_copy.copy()
        ruder_rechts_copy1 = ruder_rechts_copy.copy()
        ruder_rechts_copy2 = ruder_rechts_copy.copy()
    #forward moving oars
    #paste images of oars and ships onto each other
    
        rumpfcopy = rumpf.copy()
        
    # paste first rows of oars onto each other 
        ruder = ruder_links_copy.copy()
        ruder.paste(ruder_rechts_copy, (0, 0),ruder_rechts_copy)
        
        if j <= 2:
        # paste second row onto that
            ruder.paste(ruder_links_copy1, (10, 10),ruder_links_copy1)
            ruder.paste(ruder_rechts_copy1, (-10, 10),ruder_rechts_copy1)
    
            if j <= 1:
        # paste third row onto that
                ruder.paste(ruder_links_copy2, (20, 20),ruder_links_copy2)
                ruder.paste(ruder_rechts_copy2, (-20, 20),ruder_rechts_copy2)

        
        ruder.paste(rumpfcopy, (0, 0), rumpfcopy) 
        
        rumpfcopy = ruder
    
        rumpfcopy = rumpfcopy.resize((int(rumpfcopy.width * ratio), int(rumpfcopy.height * ratio)))
        rumpfcopy.save(os.path.join("images", "rowing_" + str(j) + "_" + str(2*frames_per_direction - i) + ".png"))
        
    #backward moving oars (add transparency to tips of oars so it seems as if they were underneath the surface of the  water)

        ruder_links_copy = ruder_links.copy()  
        
        ruder_links_copy = tips_in_water(ruder_links_copy, 1/8, "left")        
   
        ruder_links_copy = add_border(ruder_links_copy, shear_factor, 1/3)
        ruder_links_copy = shear(ruder_links_copy, shear_factor)
        
        ruder_rechts_copy = ruder_links_copy.transpose(Image.FLIP_LEFT_RIGHT)
           
    # generate extra images for second and third row of oars
    
        ruder_links_copy1 = ruder_links_copy.copy()
        ruder_links_copy2 = ruder_links_copy.copy()
        ruder_rechts_copy1 = ruder_rechts_copy.copy()
        ruder_rechts_copy2 = ruder_rechts_copy.copy()    
        
        rumpfcopy = rumpf.copy()
        
    # paste first rows of oars onto each other 
        ruder = Image.new('RGB', (rumpfcopy.width, rumpfcopy.height), (0, 0, 0))
        ruder.putalpha(0)
        ruder.paste(ruder_links_copy, (0, 0),ruder_links_copy)        
        ruder.paste(ruder_rechts_copy, (0, 0),ruder_rechts_copy)
        
        if j <= 2:
        # paste second row onto that
            ruder.paste(ruder_links_copy1, (10, 10),ruder_links_copy1)
            ruder.paste(ruder_rechts_copy1, (-10, 10),ruder_rechts_copy1)
    
            if j <= 1:
        # paste third row onto that
                ruder.paste(ruder_links_copy2, (20, 20),ruder_links_copy2)
                ruder.paste(ruder_rechts_copy2, (-20, 20),ruder_rechts_copy2)

        
        ruder.paste(rumpfcopy, (0, 0), rumpfcopy) 

        rumpfcopy = ruder
        
        rumpfcopy = rumpfcopy.resize((int(rumpfcopy.width * ratio), int(rumpfcopy.height * ratio)))
        rumpfcopy.save(os.path.join("images", "rowing_"  + str(j) + "_" + str(i + 1) + ".png"))

#processing of frames for crashing for every ship type
    
# load image of crashing wood
    crash = Image.open("images/crash.png") 
    crashcopy = crash.copy()

    crash_frames1 = 20
    for i in range(0,crash_frames1):
        
        crashcopy = crash.copy()
        crashcopy = crashcopy.resize((int(rumpfcopy.width - 2 * (crash_frames1 - i)), int(rumpfcopy.width - 2 * (crash_frames1 - i))))
        
        crashed = Image.new('RGB', (rumpfcopy.width, rumpfcopy.height), (0, 0, 0))
        crashed.putalpha(0)
        rumpf_upper = rumpfcopy.crop((0,0,rumpfcopy.width,rumpfcopy.height/2))
        rumpf_lower = rumpfcopy.crop((0,rumpfcopy.height/2,rumpfcopy.width,rumpfcopy.height))
        rumpf_upper = rumpf_upper.rotate(i)
        rumpf_lower = rumpf_lower.rotate(-i)
        crashed.paste(crashcopy, (int(crashed.width/2 - crashcopy.width/2), int(crashed.height/2 - crashcopy.height/2)), crashcopy)
        crashed.paste(rumpf_upper, (int(0), int(0)), rumpf_upper)
        crashed.paste(rumpf_lower, (int(0), int(crashed.height/2)), rumpf_lower)
        
        crashed.save(os.path.join("images", "crashing_"  + str(j) + "_" + str(i) + ".png"))

# use tips in water function to make ship sink (get more transparent)
    crash_frames2 = 20    
    for i in range(0, crash_frames2):

        crashed = tips_in_water(crashed, 1, "left", alpha = i/(crash_frames2 + 20))
        crashed.save(os.path.join("images", "crashing_"  + str(j) + "_" + str(i + crash_frames1) + ".png"))

# 2.0 create Minimap ##########################################################

# generate background tiles from original tiles by rotating and flipping
bg_wasser = Image.open('images/Hintergrund/bg_wasser.jpeg')
bg_links_oben = Image.open('images/Hintergrund/bg_links_oben.jpeg')
bg_links = Image.open('images/Hintergrund/bg_links.jpeg')
bg_rechts = Image.open('images/Hintergrund/bg_rechts.jpeg')
bg_unten = Image.open('images/Hintergrund/bg_unten.jpeg')
bg_rechts_oben = Image.open('images/Hintergrund/bg_rechts_oben.jpeg')

# put together the whole background from the tiles (for mini map)
bg_matrix = [[bg_links_oben, bg_wasser, bg_rechts_oben],
      [bg_links, bg_wasser, bg_rechts], 
      [bg_wasser, bg_unten, bg_wasser]]

minimap = Image.new('RGB', (int(bg_wasser.width * len(bg_matrix[0])), int(bg_wasser.height * len(bg_matrix))), (0, 0, 0))

for x in range(0,len(bg_matrix[1])):
    for y in range(0, len(bg_matrix)):
        minimap.paste(bg_matrix[y][x], (int((x * bg_wasser.width)), int(y * bg_wasser.height)))

# resize to mini map size
minimap = minimap.resize((int(340), int(340)))
minimap.save("images/minimap.jpeg", subsampling = 0)