from image_processing.image_processing import process_img
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

    drawing_instructions, processed_image = process_img(TEST_PICS_DIRECTORY + img_file, is_bw=0, enable_debug=1, use_test_instructions=1)

    ac = ArmController()
    ac.load_instructions(drawing_instructions)
    ac.draw_loaded_instructions()


if __name__ == '__main__':
    main()
