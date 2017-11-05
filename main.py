from image_processing.image_processing import ImageProcessor, get_test_instructions
from arm_control.arm_control import ArmController
import os


def main():
    TEST_PICS_DIRECTORY = 'pics/'

    if not os.path.exists(TEST_PICS_DIRECTORY):
        os.makedirs(TEST_PICS_DIRECTORY)

    test_pics = os.listdir(TEST_PICS_DIRECTORY)
    if len(test_pics) == 0:
        print 'No pictures found in directory pics/!'
        return

    img_file = test_pics[0]

    print 'Processing test image', img_file

    ip = ImageProcessor()
    ip.load_image(TEST_PICS_DIRECTORY + img_file)
    drawing_instructions, img_shape = ip.process_image(is_bw=1, enable_debug=1)
    #drawing_instructions, img_shape = get_test_instructions()

    #ip.get_preview_image()

    print "number of drawing_instructions =", len(drawing_instructions)

    ac = ArmController()
    ac.load_instructions(drawing_instructions, img_shape)
    ac.draw_loaded_instructions()


if __name__ == '__main__':
    main()
