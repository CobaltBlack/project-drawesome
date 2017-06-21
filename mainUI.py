from image_processing.image_processing import process_img

from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import ImageTk, Image

def openImage():
    global fileName
    fileName = askopenfilename()

    # load image
    loaded_image = ImageTk.PhotoImage(Image.open(fileName))
    
    # display image
    displayImage(loaded_image)

# CALEB ADD YOUR THINGS HERE!!!!! - JOSH
def takePicture():
    global fileName
    # TO DO: take a picture
    # i assume it would go someting like... take a picture using cam, save it in harddrive, and save the address onto 'fileName', and display it using displayImage function
    
def processImage():
    global fileName
    processed_lines, processed_image = process_img(fileName, 1, 0)

    # convert the Image object into a TkPhoto object
    im = Image.fromarray(processed_image)
    processed_image_tk = ImageTk.PhotoImage(image=im) 

    # display image
    displayImage(processed_image_tk)
    
def drawImage():
    # TO DO: start drawing with robot arm
    return
    
def displayImage(image):
    # TO DO: scale image size to fit the canvas size properly
    
    canvas.delete("all")
    canvas.image = image
    canvas.pack()
    canvas.create_image(0, 0, anchor = NW, image=image)
    

# Set up
root = Tk()
root.title("Image Processor")
root.geometry("300x300");

# Menu bar set up
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open Image", command=openImage)
filemenu.add_command(label="Take Picture", command=takePicture)
filemenu.add_command(label="Process", command=processImage)
filemenu.add_command(label="Draw", command=drawImage)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Functions", menu=filemenu)

# Canvas set up
canvas = Canvas(root, width = 1920, height = 1080)

root.config(menu=menubar)
root.mainloop()


