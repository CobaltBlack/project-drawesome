from image_processing import process_img
from os import listdir

def main():
    test_pics = listdir("./pics")

    img_file = test_pics[3]
    
    print 'Processing test image', img_file
    process_img("./pics/" + img_file)


main()
