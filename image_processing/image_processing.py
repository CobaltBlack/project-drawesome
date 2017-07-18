import cv2
import numpy as np
import random

TARGET_SCALE_LENGTH = 1000 # Length of the longer side
TARGET_ASPECT_RATIO = 16.0 / 9.0
B_INDEX = 0
G_INDEX = 1
R_INDEX = 2
MAX_BRIGHTNESS = 255
BRIGHTNESS_LEVELS = 8

COLORS = {
            'cyan':     (255,   255,    0),
            'magenta':  (255,   0,      255),
            'yellow':   (0,     255,    255),
            'white':    (255,   255,    255),
            'black':    (0,     0,      0),
         }

# One line drawing instruction
class Line:
    def __init__(self, color, points):
        self.color = color
        self.points = points




# Main image processing function
# Returns filename of drawing instructions
def process_img(filename, is_bw=1, enable_debug=0, crop_mode="fit"):

    print "Running image_processing module..."

    # Load image
    src = cv2.imread(filename)
    if src is None:
        print "File", filename, "does not exist!"
        return

    # Scale and crop image to appropriate proportions and size
    scaled = scale(src)

    # Crop or fit image into aspect ratio
    # Note to Josh: may have to move scale() code into these functions instead
    if (crop_mode == "fit"):
        cropped = fit_to_target(scaled, TARGET_SCALE_LENGTH, TARGET_ASPECT_RATIO)
    elif (crop_mode == "crop"):
        cropped = crop_to_target(scaled, TARGET_SCALE_LENGTH, TARGET_ASPECT_RATIO)

    # Detect edges
    blurred = blur(cropped)
    edges = detect_edges(blurred)

    # Use edges to detect lines
    lines = detect_outline(edges)
    if lines is None:
        print "Error: No lines found"
        wait()
        return

    # ### DEBUG IMAGE for detected lines:
    lines_detected_img = debug_detect_outline(lines, scaled.shape)

    # Fill the image by shading
    shading_lines = []
    if is_bw:
        shading_lines, shaded_img = shade_img_bw(scaled)
    else:
        shading_lines, shaded_img = shade_img_color(scaled)

    final = cv2.bitwise_and(shaded_img, lines_detected_img)

    if enable_debug:
        cv2.imshow('Original scaled', scaled)
        cv2.imshow('Outline detected', lines_detected_img)
        cv2.imshow('OUtline + shading', final)
        wait()

    return lines, final


# Scale image to targeted resolution while maintaining aspect ratio
def scale(img):

    img_h = img.shape[0]
    img_w = img.shape[1]
    ratio = 1.0
    if img_h >= img_w:
        ratio = float(TARGET_SCALE_LENGTH) / float(img_h)
    else:
        ratio = float(TARGET_SCALE_LENGTH) / float(img_w)

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

    return blurred2


# Runs Canny edge detection
def detect_edges(blurred):

    # norm = normalize_brightness(blurred)
    # cv2.imshow('Normalized 2', norm)

    edges = cv2.Canny(blurred, 50, 150)
    #edges = cv2.Canny(gray,50,150,apertureSize = 3)
    return edges


# Given Canny output, returns lines represented as:
# [
#     [[x1, y1], [x2, y2], [x3,y3]],
#     [[x1, y1], [x2, y2], [x3,y3], [x4,y4]],
#     [[x1, y1], [x2, y2]],
#     [[x1, y1], [x2, y2], [x3,y3], [x4,y4], [x5,y5]],
# ]
# where each list element is a list of coordinates representing a continuous line that passes those coordinates
#
def detect_outline(edges, min_line_length=5):
    lines = []
    adjacency = [(i, j) for i in (-1,0,1) for j in (-1,0,1) if not (i == j == 0)]

    max_y = edges.shape[0]
    max_x = edges.shape[1]

    # Scan the image from top to bottom for an "edge" pixel
    # Edge pixels are white in the Canny output
    for y in range(len(edges)):
        row = edges[y]
        for x in range(len(row)):
            pixel = row[x]
            # Skip pixels that are black (not an edge)
            if pixel == 0:
                continue

            # Once an edge pixel is found, make it black so it won't be drawn again
            edges[y][x] = 0

            # This is the start of a new line
            new_line_points = []
            new_line_points.append([x, y])

            # Repeatedly find neighbors that are also edge pixels until no more are found
            cur_x = x
            cur_y = y
            while True:
                is_next_pixel_found = False
                for dx, dy in adjacency:
                    xp = cur_x + dx
                    yp = cur_y + dy

                    # Skip if out of bounds
                    if not (0 <= xp < max_x and 0 <= yp < max_y):
                        continue

                    # Skip black pixel (not an edge)
                    adjacent_pixel = edges[yp][xp]
                    if adjacent_pixel == 0:
                        continue

                    # This is an edge pixel
                    is_next_pixel_found = True

                    # Make it black so it doesn't get found again
                    edges[yp][xp] = 0

                    # Add coordinate to the line
                    new_line_points.append([xp, yp])

                    # Update starting pixel for next iteration
                    cur_x = xp
                    cur_y = yp

                    # Don't need to check other neighbors
                    break

                # If no other edge pixel is found after checking neighbors, this is the end of the line
                if not is_next_pixel_found:
                    # Reject short lines
                    if len(new_line_points) > min_line_length:
                        new_line = Line('black', new_line_points)
                        lines.append(new_line)
                    break

                # Otherwise, continue looking for the next edge pixel

            # END WHILE TRUE LOOP
            # Repeat until no more nearby edge pixels
        # END for x loop
    # END for y loop

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



def fit_to_target(img, target_length, target_ratio):
    # TODO Josh: implement
    return img


def crop_to_target(img, target_length, target_ratio):
    # TODO Josh: implement
    return img


# Return list of lines that shades the image
# Black and white only
# Returns lines represented as:
# [
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3]]},
#     {color: 'black', points: [[x1, y1], [x2, y2]},
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3], [x4,y4]]},
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3]]},
# ]
# Where x1, y1... etc are the coordinates for each point in a line.
# The line is the points connected together
def shade_img_bw(src):


    # Reduce bit depth
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    diff = 256 / BRIGHTNESS_LEVELS # difference between brightness levels
    gray = (gray / diff) * diff
    #cv2.imshow('depth reduced', gray)

    all_hatches = np.zeros(gray.shape, np.uint8)
    all_hatches[:] = 0

    canvas = np.zeros(src.shape, np.uint8)
    canvas[:,:] = (255, 255, 255)

    lines = []

    # For each brightness level, replace it with crosshatches
    for i in range(BRIGHTNESS_LEVELS):

        # Isolate the current brightness level using thresholds
        brightness = i * diff
        if brightness != 0:
            # Change colors above the current brightness to 0
            ret, thresh = cv2.threshold(gray, brightness+1, MAX_BRIGHTNESS, cv2.THRESH_TOZERO_INV)
            # Reduce the rest brightness colors below
            ret, thresh2 = cv2.threshold(thresh, brightness-1, MAX_BRIGHTNESS, cv2.THRESH_BINARY)
        else:
            ret, thresh2 = cv2.threshold(gray, brightness + 1, MAX_BRIGHTNESS, cv2.THRESH_BINARY_INV)

        # Only crosshatch if it's not the brightest level
        if i < (BRIGHTNESS_LEVELS - 1):
            # Increase hatch spacing quadratically by squaring
            hatch_spacing = ((i+2) ** 2) + 3
            crosshatch = gen_crosshatch(thresh2.shape, int(hatch_spacing), TARGET_SCALE_LENGTH)

            # Shape the hatching using the shape of the brightness threshold
            # bitwise-AND the cross hatch and threshold brightness
            anded = cv2.bitwise_and(thresh2, crosshatch)

            # Conversion to Line instructions using houghlines
            hough_lines = cv2.HoughLinesP(anded, 1, np.pi/180, 10, minLineLength=4, maxLineGap=0)
            if len(hough_lines) > 0:
                for line in hough_lines:
                    lines.append(line)

                    # Draw the lines on a blank canvas for debug/testing
                    x1, y1, x2, y2 = line[0]
                    cv2.line(canvas, (x1,y1), (x2,y2), (0,0,0), 1)


            all_hatches = cv2.bitwise_or(anded, all_hatches)

            #cv2.imshow("anded_" + str(brightness), anded)

    # end for-loop

    all_hatches = 255 - all_hatches

    print 'len(lines)', len(lines)

    all_hatches_bgr = cv2.cvtColor(all_hatches, cv2.COLOR_GRAY2BGR)
    #cv2.imshow("all_hatches_" + str(brightness), all_hatches_bgr)
    #cv2.imshow("all_hatches converted into hough lines", canvas)
    return lines, canvas


# Return list of lines that shades the image
# Returned lines use CMYK colors
def shade_img_color(src):
    # Shade using alternating color/black
    # Color hue is whichever of the base colors it is the closest to
    # Higher saturation: More color lines, low sat: less color
    # Higher value: more "blanks" (less lines), Low value: more black lines

    print "shade_img_color start"

    canvas = np.zeros(src.shape, np.uint8)
    canvas[:,:] = (255, 255, 255)

    lines = []

    # Convert image into 1-channel CMYK images (Cyan, Magenta, Yellow, Black)
    c_img, m_img, y_img, k_img = rgb_to_cmyk_imgs(src)
    for img, color in [[c_img, 'cyan'], [m_img, 'magenta'], [y_img, 'yellow'], [k_img, 'black']]:

        # Reduce bit depth per channel
        diff = 256 / BRIGHTNESS_LEVELS # diff is difference between brightness levels
        reduced = (img / diff) * diff
        cv2.imshow("Reduced " + color, reduced)

         # For each brightness level, replace it with crosshatches
        for i in range(BRIGHTNESS_LEVELS):

            # Isolate the current brightness level using thresholds
            brightness = i * diff
            if brightness != 0:
                # Change colors above the current brightness to 0
                ret, thresh = cv2.threshold(reduced, brightness+1, MAX_BRIGHTNESS, cv2.THRESH_TOZERO_INV)
                # Reduce the rest brightness colors below
                ret, thresh2 = cv2.threshold(thresh, brightness-1, MAX_BRIGHTNESS, cv2.THRESH_BINARY)
            else:
                ret, thresh2 = cv2.threshold(reduced, brightness + 1, MAX_BRIGHTNESS, cv2.THRESH_BINARY_INV)

            # Only crosshatch if it's not the brightest level
            if i < (BRIGHTNESS_LEVELS - 1):
                # Increase hatch spacing quadratically by squaring
                hatch_spacing = ((i+2) ** 2) + 5

                # Use varying angles of cross hatches for each color
                rotation = i * (TARGET_SCALE_LENGTH / BRIGHTNESS_LEVELS)


                crosshatch = gen_crosshatch(thresh2.shape, int(hatch_spacing), rotation)
#random.randint(0, TARGET_SCALE_LENGTH*0.9)
                # Shape the hatching using the shape of the brightness threshold
                # bitwise-AND the cross hatch and threshold brightness
                anded = cv2.bitwise_and(thresh2, crosshatch)

                # Conversion to Line instructions using houghlines
                hough_lines = cv2.HoughLinesP(anded, 1, np.pi/180, 10, minLineLength=4, maxLineGap=0)
                if hough_lines is None:
                    print "No lines found", color, "brightness:", i
                elif len(hough_lines) > 0:
                    for line in hough_lines:
                        lines.append(line)

                        # Draw the lines on a blank canvas for debug/testing
                        x1, y1, x2, y2 = line[0]
                        cv2.line(canvas, (x1,y1), (x2,y2), COLORS[color], 1)
        # end for-loop

    # end for-loop

    cv2.imshow("CMYK into hough lines", canvas)

    return [], canvas



    # Converts RGB src image into 4 one-channel images, for each of C, Y, M, K
def rgb_to_cmyk_imgs(src):

    print "Converting image to CMYK..."

    img_shape = (src.shape[0], src.shape[1])

    # Initialize 4 one-channel images for C, M, Y, K
    c_img = np.zeros(img_shape, np.uint8)
    m_img = np.zeros(img_shape, np.uint8)
    y_img = np.zeros(img_shape, np.uint8)
    k_img = np.zeros(img_shape, np.uint8)

    for y in range(len(src)):
        row = src[y]
        for x in range(len(row)):
            pixel_b = src.item(y,x,B_INDEX)
            pixel_g = src.item(y,x,G_INDEX)
            pixel_r = src.item(y,x,R_INDEX)

            c_val, m_val, y_val, k_val = rgb_to_cmyk(pixel_r, pixel_g, pixel_b)

            for img in [c_img, m_img, y_img, k_img]:
                c_img.itemset((y,x), 255-c_val)
                m_img.itemset((y,x), 255-m_val)
                y_img.itemset((y,x), 255-y_val)
                k_img.itemset((y,x), 255-k_val)

    print "Done."
    return c_img, m_img, y_img, k_img


cmyk_scale = 255

def rgb_to_cmyk(r,g,b):
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / 255.
    m = 1 - g / 255.
    y = 1 - b / 255.

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0,cmyk_scale]
    return c*cmyk_scale, m*cmyk_scale, y*cmyk_scale, k*cmyk_scale


# shape: shape of output
# spacing:  number of pixels between each line
# rotation: angle in radians to tilt the entire hatchingf
# Returns a picture
def gen_crosshatch(shape, spacing, rotation, is_bw=1):
    if spacing < 1:
        print "Crosshatch spacing too small!"
        return

    offset = 0 # spacing / 3

    # Make canvas
    canvas = np.zeros(shape, np.uint8)
    canvas[:,:] = 0

    # Random rotation (CHANGE THIS VALUE BETWEEN 0 - TARGET_SCALE_LENGTH FOR DESIRED ROTATION. TARGET_SCALE_LENGTH = "+", 0 = "x".
    rnd_rotation = rotation #TARGET_SCALE_LENGTH # random.randint(0, TARGET_SCALE_LENGTH*0.9)

    # Draw the lines on a blank canvas
    for i in range((TARGET_SCALE_LENGTH/spacing)*2):
        # parallel lines
        x1 = 0
        y1 = i * spacing + random.randint(-offset, offset)
        x2 = TARGET_SCALE_LENGTH
        y2 = i * spacing + random.randint(-offset, offset) + (rnd_rotation - TARGET_SCALE_LENGTH)
        cv2.line(canvas, (x1,y1), (x2,y2), 255, 1)

        # perpendicular lines
        x1 = 0
        y1 = i * spacing + random.randint(-offset, offset)
        x2 = TARGET_SCALE_LENGTH
        y2 = i * spacing + random.randint(-offset, offset) + (TARGET_SCALE_LENGTH - rnd_rotation)

        cv2.line(canvas, (y2-TARGET_SCALE_LENGTH, x2),(y1-TARGET_SCALE_LENGTH, x1), 255, 1)

    # save image as cache, so it doesn't have to be processed again?
    cv2.imwrite('crosshatch_' + str(spacing) + "_" + str(rotation) + ".jpg", canvas)

    return canvas

# DEBUG IMAGE for detected lines:
def debug_detect_outline(lines, shape):
    # Draw the lines on a blank canvas
    canvas = np.zeros(shape, np.uint8)
    canvas[:,:] = (255, 255, 255)

    for i, line in enumerate(lines):
        # Make a HSV color for the line
        hue = int( ( float(i) / len(lines) ) * 255 )
        #hue = random.randint(0, 255)
        val = 0
        sat = 255
        for j, coord in enumerate(line.points):
            #x, y = coord.x, coord.y
            #cv2.line(canvas, (x1,y1), (x2,y2), (0,0,0), 2)
            # Make the HSV color and convert to RGB
            col_hsv = (hue, sat, val)
            col_bgr = cv2.cvtColor(np.array([[col_hsv]], np.uint8), cv2.COLOR_HSV2BGR)[0][0]

            # Update the pixel
            canvas[coord[1]][coord[0]] = col_bgr

    return canvas

# Allows image to be displayed
def wait():
	cv2.waitKey()
	cv2.destroyAllWindows()
