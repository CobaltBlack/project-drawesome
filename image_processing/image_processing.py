import cv2
import numpy as np
import random

# Main image processing function
# Returns filename of drawing instructions
def process_img(filename, is_bw=1):
    
    # Load image
    src = cv2.imread(filename)
    if src is None:
        print "File", filename, "does not exist!"
        return
           
    # Scale and crop image to appropriate proportions and size
    scaled = scale(src)
    
    blurred = blur(scaled)
    
    # Detect edges
    edges = detect_edges(blurred)
    
    # Use edges to detect lines
    lines = detect_lines(edges)
    if lines is None:
        print "Error: No lines found"
        wait()
        return
    
    # Draw the lines on a blank canvas
    canvas = np.zeros(scaled.shape, np.uint8)
    canvas[:,:] = (255, 255, 255)
    print "Number of lines:", len(lines)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(canvas, (x1,y1), (x2,y2), (0,0,0), 2)
    
    
    shading_lines = []
    if is_bw:
        shading_lines, shaded_img = shade_img_bw(blurred)
    else:
        shading_lines = shade_img_color(blurred)

    
    final = cv2.bitwise_and(shaded_img, canvas)
        
    cv2.imshow('Edges', edges)
    cv2.imshow('Lines drawn', canvas)
    cv2.imshow('Lines drawn with shade', final)
    wait()


# Scale image to targeted resolution while maintaining aspect ratio
def scale(img):
    
    target_length = 500.0
    img_h = img.shape[0]
    img_w = img.shape[1]
    ratio = 1.0
    if img_h >= img_w:
        ratio = target_length / img_h
    else:
        ratio = target_length / img_w
    
    new_h = int(img_h * ratio)
    new_w = int(img_w * ratio)
    scaled = cv2.resize(img, (new_w, new_h))
    
    print "Source dimension is", img.shape
    print "Scaled dimension is ", scaled.shape
    
    return scaled


# Blurs the image for edge detection
def blur(img):

    # Gaussian Blur
    blur_kernel_size = 5 # must be odd. larger -> more blur.
    blurred = cv2.GaussianBlur(img, (blur_kernel_size, blur_kernel_size), 0)
    
    blurred2 = cv2.bilateralFilter(blurred, 7, 75, 75)
    cv2.imshow('Bilateral filtered', blurred2)
    
    return blurred2


# Runs Canny edge detection
def detect_edges(blurred):
    
    # norm = normalize_brightness(blurred)
    # cv2.imshow('Normalized 2', norm)
    
    edges = cv2.Canny(blurred, 50, 150)
    #edges = cv2.Canny(gray,50,150,apertureSize = 3)
    return edges
    

# Given Canny output, returns lines represented as:
#
#
#
# TODO: implement new algo
def detect_lines(edges):
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, 20, minLineLength=2, maxLineGap=2)
    return lines
    
    
# Do something by converting to another color space
# Not too useful    
def normalize_brightness(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    for row in hsv:
        for pixel in row:
            pixel[1] = 255
        
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    
    return bgr
    
    
# Return list of lines that shades the image
# Black and white only
def shade_img_bw(src):
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    print gray.shape
    
    # Reduce bit depth
    max_val = 255
    brightness_levels = 8
    diff = 256 / brightness_levels # difference between brightness levels
    gray = (gray / diff) * diff
    cv2.imshow('depth reduced', gray)
    
    all_hatches = np.zeros(gray.shape, np.uint8)
    all_hatches[:] = 0
    
    # For each brightness level, replace it with crosshatches
    # Isolate each brightness level using thresholds
    for i in range(brightness_levels):
        brightness = i * diff
        if brightness != 0:
            # Change colors above the current brightness to 0
            ret, thresh = cv2.threshold(gray, brightness+1, max_val, cv2.THRESH_TOZERO_INV)
            # Reduce the rest brightness colors below 
            ret, thresh2 = cv2.threshold(thresh, brightness-1, max_val, cv2.THRESH_BINARY)
        else:
            ret, thresh2 = cv2.threshold(gray, brightness + 1, max_val, cv2.THRESH_BINARY_INV)
        cv2.imshow("thresh2" + str(brightness), thresh2)
        
        # Only crosshatch if it's not the brightest level
        if i < (brightness_levels - 2):
            # Increase hatch spacing quadratically
            hatch_spacing = ((i+1) ** 2) + 2
            crosshatch = gen_crosshatch(thresh2.shape, hatch_spacing, 0)
                    
            # Shape the hatching using the shape of the brightness threshold
            # AND the cross hatch and threshold brightness
            anded = cv2.bitwise_and(thresh2, crosshatch)
            all_hatches = cv2.bitwise_or(anded, all_hatches)
        
            #cv2.imshow("anded_" + str(brightness), anded)
    
    # end for-loop
    
    all_hatches = 255 - all_hatches
    all_hatches_bgr = cv2.cvtColor(all_hatches, cv2.COLOR_GRAY2BGR)
    cv2.imshow("all_hatches_" + str(brightness), all_hatches_bgr)
        
    lines = []
    return lines, all_hatches_bgr


# Return list of lines that shades the image
# BACKLOG: colored version 
def shade_img_color(src):
    return []
    
    
# shape: shape of output        
# spacing:  number of pixels between each line
# rotation: angle in radians to tilt the entire hatchingf
# Returns a picture
def gen_crosshatch(shape, spacing, rotation, is_bw=1):
    if spacing < 1:
        print "Crosshatch spacing too small!"
        return
        
    offset = spacing / 3
        
    # Make canvas
    canvas = np.zeros(shape, np.uint8)
    canvas[:,:] = 0
    
    # Draw the lines on a blank canvas
    for i in range(500/spacing):
        # horizontal lines
        x1 = 0
        y1 = i * spacing + random.randint(-offset, offset)
        x2 = 500
        y2 = i * spacing + random.randint(-offset, offset)
        cv2.line(canvas, (x1,y1), (x2,y2), 255, 1)
        
        # vertical lines
        y1 = i * spacing + random.randint(-offset, offset)
        y2 = i * spacing + random.randint(-offset, offset)
        cv2.line(canvas, (y1, x1), (y2, x2), 255, 1)
        
    # TODO: Rotate picture by random amount
        
    # save image as cache, so it doesn't have to be processed again?
    #cv2.imwrite('crosshatch_' + str(spacing) + ".jpg", canvas)
        
    return canvas
    
# Allows image to be displayed
def wait():
	cv2.waitKey()
	cv2.destroyAllWindows()
