import cv2
import numpy as np
import os

def main():

    # Replace this accordingly
    TEST_PICS_DIRECTORY = 'cache/'

    if not os.path.exists(TEST_PICS_DIRECTORY):
        os.makedirs(TEST_PICS_DIRECTORY)

    test_pics = os.listdir(TEST_PICS_DIRECTORY)
    if len(test_pics) == 0:
        print 'No pictures found in directory pics/!'
        return

    img_file = test_pics[1] #'crosshatch_69_750.jpg'# test_pics[1]

    print 'Processing test image', img_file

    # Load image
    src = cv2.imread(TEST_PICS_DIRECTORY + img_file)
    if src is None:
        print "File", filename, "does not exist!"
        return

    canvas = np.zeros(src.shape, np.uint8)
    canvas[:,:] = (255, 255, 255)
    
    gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
    
    hough_lines = cv2.HoughLinesP(gray, 1, np.pi/360, 200, minLineLength=15, maxLineGap=1)
    if hough_lines is None:
        print "No lines found", "brightness:"
    elif len(hough_lines) > 0:
        for line in hough_lines:
            #lines.append(line)

            # Draw the lines on a blank canvas for debug/testing
            x1, y1, x2, y2 = line[0]
            cv2.line(canvas, (x1,y1), (x2,y2), (0,0,0), 1)

    cv2.imshow("Source", src)
    cv2.imshow("Hough lines", canvas)
    wait()
    

# Allows image to be displayed
def wait():
	cv2.waitKey()
	cv2.destroyAllWindows()

	
if __name__ == '__main__':
    main()
