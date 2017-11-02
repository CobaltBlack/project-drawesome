'''
image_processing.py

This file converts the raw camera image into drawing instructions for the robot arm to follow.
It creates lines for drawing detected edges, and for shading the brightness/color
'''

import cv2
import math
import numpy as np
import random

TARGET_SCALE_LENGTH = 1000 # Length of the longer side
TARGET_ASPECT_RATIO = 16.0 / 9.0
LETTER_RATIO = 8.5 / 11.0

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

COLOR_TO_ANGLE = {
            'cyan':     15,
            'magenta':  75,
            'yellow':   0,
            'black':    45,
}


# One line drawing instruction
class Line:

    def __init__(self, color, points):
        self.color = color
        self.points = points
        self.is_reversed = False


    def get_points(self):
        if self.is_reversed:
            return reversed(self.points)

        return self.points


class ImageProcessor:

    def __init__(self):
        print ("Initializing ImageProcessor...")
        self.is_image_loaded = False
        self.is_image_processed = False


    def load_image(self, filename):
        print "Loading", filename
        self.src = cv2.imread(filename)
        if self.src is None:
            print "File", filename, "does not exist!"
            return False

        self.is_image_loaded = True
        self.is_image_processed = False

        return True


    def process_image(self, is_bw=1, enable_debug=0, crop_mode="fit", use_test_instructions=0):
        if not self.is_image_loaded:
            print "Error: No image is not loaded!"
            return

        # Scale and crop image to appropriate proportions and size
        self.scaled = scale(self.src, TARGET_SCALE_LENGTH)

        # Crop or fit image into aspect ratio
        # if (crop_mode == "fit"):
            # self.cropped = fit_to_target(self.scaled, TARGET_SCALE_LENGTH, LETTER_RATIO)
        # elif (crop_mode == "crop"):
            # self.cropped = crop_to_target(self.scaled, TARGET_SCALE_LENGTH, LETTER_RATIO)

        # Detect edges
        self.blurred = blur(self.scaled)
        self.edges = detect_edges(self.blurred)

        # Use edges to detect lines
        lines = detect_outline(self.edges)
        if lines is None:
            print "Error: No lines found"
            wait()
            return

        lines = sort_lines_by_distance(lines)
        total_dist, avg_dist = calc_interline_distance(lines)
        print "Outline only: Total Dist =", total_dist, "Avg Dist =", avg_dist

        # ### DEBUG IMAGE for detected lines:
        lines_detected_img = debug_detect_outline(lines, self.scaled.shape)

        # Fill the image by shading
        shading_lines = []
        if is_bw:
            shading_lines, shaded_img = shade_img_bw(self.scaled)
        else:
            shading_lines, shaded_img = shade_img_color(self.scaled)

        lines.extend(shading_lines)

        total_dist, avg_dist = calc_interline_distance(lines)
        print "Outline + Shading: Total Dist =", total_dist, "Avg Dist =", avg_dist

        self.preview_line_image = cv2.bitwise_and(shaded_img, lines_detected_img)

        self.is_image_processed = True

        if enable_debug:
            # cv2.imshow('Original scaled', cropped)
            # cv2.imshow('Outline detected', lines_detected_img)
            cv2.imshow('OUtline + shading', self.preview_line_image)
            wait()

        return lines



    def get_preview_image(self):
        if self.is_image_processed:
            return self.preview_line_image
        return []


    def get_source_image(self):
        return self.src


# end class ImageProcessor

'''
# Main image processing function
# Returns array of line drawing instructions
def process_img(filename, is_bw=1, enable_debug=0, crop_mode="fit", use_test_instructions=0):

    print "Running image_processing module..."

    # Test instructions
    if use_test_instructions:
        print "Returning test instructions!"
        return get_test_instructions(), []

    # Load image
    src = cv2.imread(filename)
    if src is None:
        print "File", filename, "does not exist!"
        return

    # Scale and crop image to appropriate proportions and size
    scaled = scale(src)

    # Crop or fit image into aspect ratio
    if (crop_mode == "fit"):
        cropped = fit_to_target(scaled, TARGET_SCALE_LENGTH, LETTER_RATIO)
    elif (crop_mode == "crop"):
        cropped = crop_to_target(scaled, TARGET_SCALE_LENGTH, LETTER_RATIO)

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
    lines_detected_img = debug_detect_outline(lines, cropped.shape)

    # Fill the image by shading
    shading_lines = []
    if is_bw:
        shading_lines, shaded_img = shade_img_bw(cropped)
    else:
        shading_lines, shaded_img = shade_img_color(cropped)

    lines.extend(shading_lines)

    final = cv2.bitwise_and(shaded_img, lines_detected_img)

    if enable_debug:
        cv2.imshow('Original scaled', cropped)
        cv2.imshow('Outline detected', lines_detected_img)
        cv2.imshow('OUtline + shading', final)
        wait()

    return lines, final
'''

# Scale image to targeted resolution while maintaining aspect ratio
def scale(img, target_length):

    img_h = img.shape[0]
    img_w = img.shape[1]
    ratio = 1.0
    if img_h >= img_w:
        ratio = float(target_length) / float(img_h)
    else:
        ratio = float(target_length) / float(img_w)

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

    edges = cv2.Canny(blurred, 50, 150)
    return edges


# Given Canny output,
# Returns lines represented as:
# [
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3]]},
#     {color: 'black', points: [[x1, y1], [x2, y2]},
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3], [x4,y4]]},
#     {color: 'black', points: [[x1, y1], [x2, y2], [x3,y3]]},
# ]
# where each list element is a list of coordinates representing a continuous line that passes those coordinates
#
def detect_outline(edges, min_line_length=5, return_only_endpoints=0, color='black'):

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
                    if edges[yp][xp] == 0:
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
                        if (return_only_endpoints):
                            endpoints = (new_line_points[0], new_line_points[-1])
                            new_line = Line(color, endpoints)

                        else:
                            new_line = Line(color, new_line_points)

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
    img_h, img_w = img.shape[:2]
    IMG_RATIO = img_w / img_h

    color = [255, 255, 255] # rgb white

    if target_ratio >= IMG_RATIO:
        target_h = img_w / target_ratio
        bordersize = int(round((img_h - target_h)/2))
        border_img = cv2.copyMakeBorder(img, top=0, bottom=0, left=bordersize, right=bordersize, borderType= cv2.BORDER_CONSTANT, value=color)
        return border_img

    else:
        target_w = img_h * target_ratio
        bordersize = int(round((img_w - target_w)/2))
        border_img = cv2.copyMakeBorder(img, top=bordersize, bottom=bordersize, left=0, right=0, borderType= cv2.BORDER_CONSTANT, value=color)
        return border_img


def crop_to_target(img, target_length, target_ratio):
    img_h, img_w = img.shape[:2]
    IMG_RATIO = img_w / img_h

    if target_ratio >= IMG_RATIO:
        target_h = img_w / target_ratio
        cropped_h = (img_h - target_h)/2
        crop_img = img[int(round(cropped_h)):int(round(target_h + cropped_h)), 0:img_w]
        return crop_img

    else:
        target_w = img_h * target_ratio
        cropped_w = (img_w - target_w)/2
        crop_img = img[0:img_h, int(round(cropped_w)):int(round(target_w + cropped_w))]
        return crop_img


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

    all_hatches = np.zeros(gray.shape, np.uint8)
    all_hatches[:] = 0

    hatch_canvas = np.zeros(gray.shape, np.uint8)
    hatch_canvas[:] = 0

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
            crosshatch = gen_crosshatch(thresh2.shape, int(hatch_spacing), 45)

            # Shape the hatching using the shape of the brightness threshold
            # bitwise-AND the cross hatch and threshold brightness
            cropped_hatch = cv2.bitwise_and(thresh2, crosshatch)

            # Add these cropped hatches to a temp canvas
            hatch_canvas = cv2.bitwise_or(hatch_canvas, cropped_hatch)

            # Repeat for hatches in perpendicular direction
            #crosshatch_perp = gen_crosshatch(thresh2.shape, int(hatch_spacing), get_perpendicular_angle(45))
            #cropped_hatch_perp = cv2.bitwise_and(thresh2, crosshatch_perp)
            #detected_lines_perp = detect_outline(cropped_hatch_perp, return_only_endpoints=1)
            #lines.extend(detected_lines_perp)

    # end for-loop

    # Detect lines on aggregation of all hatches
    detected_lines = detect_outline(hatch_canvas, return_only_endpoints=1)

    # Sort to minimize pen-up distance
    sorted_lines = sort_lines_by_distance(detected_lines)

    # Add lines to main list
    lines.extend(sorted_lines)

    print 'Shading len(lines)', len(lines)

    debug_img = debug_detect_outline(lines, src.shape, endpoints_only=1)

    return lines, debug_img


# Return list of lines that shades the image
# Returned lines use CMYK colors
def shade_img_color(src):
    # IDEAS:
    # Shade using alternating color/black
    # Color hue is whichever of the base colors it is the closest to
    # Higher saturation: More color lines, low sat: less color
    # Higher value: more "blanks" (less lines), Low value: more black lines

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

        # Use varying angles of cross hatches for each color
        rotation = COLOR_TO_ANGLE[color]
        rotation_perp = get_perpendicular_angle(rotation)

        # Temp canvas to hold hatches for processing later
        hatch_canvas = np.zeros(c_img.shape, np.uint8)
        hatch_canvas[:] = 0
        hatch_canvas_perp = np.zeros(c_img.shape, np.uint8)
        hatch_canvas_perp[:] = 0

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
                crosshatch = gen_crosshatch(thresh2.shape, int(hatch_spacing), rotation)

                # Shape the hatching using the shape of the brightness threshold
                # bitwise-AND the cross hatch and threshold brightness
                cropped_hatch = cv2.bitwise_and(thresh2, crosshatch)

                # Add these cropped hatches to a temp canvas
                hatch_canvas = cv2.bitwise_or(hatch_canvas, cropped_hatch)

                # Repeat for hatches in perpendicular direction
                # Don't do this for black lines because it looks shitty
                if color != 'black':
                    crosshatch_perp = gen_crosshatch(thresh2.shape, int(hatch_spacing), rotation_perp)
                    cropped_hatch_perp = cv2.bitwise_and(thresh2, crosshatch_perp)
                    hatch_canvas_perp = cv2.bitwise_or(hatch_canvas_perp, cropped_hatch_perp)

        # end for-loop

        # Detect lines from both sets of cropped hatches
        detected_lines = detect_outline(hatch_canvas, return_only_endpoints=1, color=color)

        # Cross hatch with perpendicular lines for CMY
        # (not black lines cuz it looks bad)
        if color != 'black':
            detected_lines_perp = detect_outline(hatch_canvas_perp, return_only_endpoints=1, color=color)
            detected_lines.extend(detected_lines_perp)

        # Sort to minimize pen-up distance
        sorted_lines = sort_lines_by_distance(detected_lines)
        lines.extend(sorted_lines)


    # end for-loop

    print 'len(lines) from shade_img_color', len(lines)

    debug_img = debug_detect_outline(lines, src.shape, endpoints_only=1)

    return lines, debug_img


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

    print "Done converting image to CMYK"
    return c_img, m_img, y_img, k_img


cmyk_scale = 255

def rgb_to_cmyk(r, g, b):
    if (r == 0) and (g == 0) and (b == 0):
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / 255.
    m = 1 - g / 255.
    y = 1 - b / 255.

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    divisor = 1 - min_cmy
    c = (c - min_cmy) / divisor
    m = (m - min_cmy) / divisor
    y = (y - min_cmy) / divisor
    k = min_cmy

    # rescale to the range [0,cmyk_scale]
    return c*cmyk_scale, m*cmyk_scale, y*cmyk_scale, k*cmyk_scale


# shape:    shape of output
# spacing:  number of pixels for spacing between each line
# rotation: angle in degrees to tilt all the lines. 0 for horizontal, 90 for vertical
# Returns a picture
def gen_crosshatch(shape, spacing, rotation, is_bw=1):

    if spacing < 1:
        print "Crosshatch spacing too small!"
        return

    height = shape[0]
    width = shape[1]
    longer_side = height if (height > width) else width

    # Make canvas
    canvas = np.zeros((height, width), np.uint8)
    canvas[:,:] = 0

    # Make rotation between 0 and 180
    while (rotation > 180):
        rotation = rotation % 180

    while (rotation < 0):
        rotation = rotation + 180

    # Half of the angles can be mirrored
    is_mirrored = False
    if (rotation > 90):
        is_mirrored = True
        rotation = 180 - rotation

    pheta = math.radians(rotation)
    if (rotation == 0):
        # Horizontal lines
        for y in xrange(0, height, spacing):
            cv2.line(canvas, (0, y), (width, y), 255, 1)

    elif (rotation == 90):
        # Vertical lines
        for x in xrange(0, width, spacing):
            cv2.line(canvas, (x, 0), (x, height), 255, 1)

    elif (rotation < 45):
        # Draw lines that begin from the left edge, and slopes upwards
        # the " * 2 " so that some lines start from outside and beneath the image, and slope into the image
        for y_start in xrange(0, longer_side * 2, spacing):
            x_start = 0
            x_end = float(y_start) / math.tan(pheta)
            y_end = 0

            x_start_draw = int(x_start)
            y_start_draw = int(y_start)
            x_end_draw = int(x_end)
            y_end_draw = int(y_end)

            # If x_end extends beyond the width
            if (x_end >= width):
                # Find new y-intercept at the right border
                y_end_draw = int(y_start - (float(y_start) / float(x_end)) * width)
                x_end_draw = int(width - 1)
                if (y_end_draw >= height):
                    break

            # If y_start extends beyond bottom border
            if (y_start >= height):
                # Find new x-intercept at the bottom border
                x_start_draw = int( (1 - float(height) / float(y_start) ) * x_end )
                y_start_draw = int(height - 1)
                if (x_start_draw >= width):
                    break

            if is_mirrored:
                x_start_draw = width - x_start_draw
                x_end_draw = width - x_end_draw

            cv2.line(canvas, (x_start_draw, y_start_draw), (x_end_draw, y_end_draw), 255, 1)

    elif (rotation >= 45 and rotation < 90):
        # Draw lines that start from top border, slopes into left edge
        for x_start in xrange(0, longer_side * 2, spacing):
            y_start = 0
            x_end = 0
            y_end = x_start * math.tan(pheta)

            x_start_draw = int(x_start)
            y_start_draw = int(y_start)
            x_end_draw = int(x_end)
            y_end_draw = int(y_end)

            if (y_end >= height):
                x_end_draw = int( x_start * ( 1 - float(height) / float(y_end) ) )
                y_end_draw = height
                if x_end_draw > width:
                    break

            # If x_start is beyond right border
            if (x_start > width):
                y_start_draw = int( y_end * ( 1 - float(width)/float(x_start)) )
                x_start_draw = width
                if y_start_draw > height:
                    break

            if is_mirrored:
                x_start_draw = width - x_start_draw
                x_end_draw = width - x_end_draw

            cv2.line(canvas, (x_start_draw, y_start_draw), (x_end_draw, y_end_draw), 255, 1)

    else:
        print "Rotation value is invalid:", rotation

    return canvas


# Returns a list of lines with same size, but ordered such that the distance between the end and start of the next line is minimized (minimizes the distance that the arm has to travel with the pen up)
def sort_lines_by_distance(lines):
    num_lines = len(lines)
    if num_lines == 0:
        return []

    sorted_lines = []
    sorted_lines.append(lines[0])

    while(len(lines) > 1):
        # Get endpoint of line
        curr_line = sorted_lines[-1]
        curr_endpoint = curr_line.points[-1]

        # Find line whose start or end point is closest to current endpoint
        closest_line = lines[0]
        closest_line_index = 0
        curr_min_dist = float("inf")
        is_reversed = False
        for i in range(len(lines)):
            next_line = lines[i]
            next_start = next_line.points[0]
            next_end = next_line.points[-1]

            dist_to_start = dist_points(curr_endpoint, next_start)
            if (dist_to_start < curr_min_dist):
                curr_min_dist = dist_to_start
                closest_line = next_line
                closest_line_index = i
                is_reversed = False

            dist_to_end = dist_points(curr_endpoint, next_end)
            if (dist_to_end < curr_min_dist):
                curr_min_dist = dist_to_end
                closest_line = next_line
                closest_line_index = i
                is_reversed = True

        # If endpoint is closest, draw the line in reverse
        if is_reversed:
            closest_line.points = list(reversed(closest_line.points))

        # Add line as next instruction to draw
        sorted_lines.append(closest_line)

        # Remove line from original list so it does not get found again
        lines.pop(closest_line_index)

    assert (num_lines == len(sorted_lines))
    return sorted_lines


# Calculates distances between the end and start of next line
def calc_interline_distance(lines):
    total_dist = 0
    num_lines = len(lines)

    curr_endpoint = lines[0].points[-1]

    for line in lines:
        next_start_point = line.points[0]
        dist_to_next_line = dist_points(curr_endpoint, next_start_point)
        total_dist = total_dist + dist_to_next_line
        curr_endpoint = line.points[-1]

    return total_dist, total_dist / num_lines


# DEBUG IMAGE for detected lines:
def debug_detect_outline(lines, shape, endpoints_only=0):

    # Draw the lines on a blank canvas
    canvas = np.zeros(shape, np.uint8)
    canvas[:,:] = (255, 255, 255)

    for i, line in enumerate(lines):

        if not endpoints_only:
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

        else:
            # Make line using the endpoints
            start_point =  (line.points[0][0], line.points[0][1])
            end_point =  (line.points[1][0], line.points[1][1])
            thickness = 2
            if (line.color == 'black'):
                thickness = 1

            cv2.line(canvas, start_point, end_point, COLORS[line.color], thickness)

    return canvas


# Allows image to be displayed
def wait():
	cv2.waitKey()
	cv2.destroyAllWindows()

def get_perpendicular_angle(degrees):
    while (degrees > 180):
        degrees = degrees % 180

    while (degrees < 0):
        degrees = degrees + 180

    return degrees + 90


def get_test_instructions():
    lines = []

    color = 'black'

    # Vertical line
    points = []
    points.append([0,  0])
    points.append([0, 200])
    points.append([0, 400])
    points.append([0, 600])
    points.append([0, 800])
    points.append([0, 1000])
    points.append([0, 1200])
    points.append([0, 1400])
    points.append([0, 1600])
    test_line = Line(color, points)
    lines.append(test_line)

    # Horizontal line
    points = []
    points.append([  0, 150])
    points.append([300, 150])
    test_line = Line(color, points)
    lines.append(test_line)

    # Diagonal lines
    points = []
    points.append([  0,   0])
    points.append([300, 300])
    test_line = Line(color, points)
    lines.append(test_line)

    points = []
    points.append([300,   0])
    points.append([  0, 300])
    test_line = Line(color, points)
    lines.append(test_line)

    return lines


def dist_points(p1, p2):
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])
    return math.sqrt(dy**2 + dx**2)

