from image_processing import process_img
from os import listdir

# Replace this accordingly
TEST_PICS_DIRECTORY = 'D:/Eric/Git/test_pics/'

def main():
    test_pics = listdir(TEST_PICS_DIRECTORY)

    img_file = test_pics[1]
    
    print 'Processing test image', img_file
    process_img(TEST_PICS_DIRECTORY + img_file)


main()
