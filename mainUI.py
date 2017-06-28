from image_processing.image_processing import process_img

from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import ImageTk, Image

def open_image():
    global file_name
    
    file_name = askopenfilename()
    
    if not file_name:
        print "Open image canceled!"
        return
    
    loaded_image = ImageTk.PhotoImage(Image.open(file_name))
    display_image(loaded_image)

# CALEB ADD YOUR THINGS HERE!!!!! - JOSH
def take_picture():
    global file_name
    
    # TO DO: take a picture
    # i assume it would go someting like... take a picture using cam, save it in harddrive, and save the address onto 'file_name', and display it using 'display_image' function
    
def process_image():
    global file_name
    
    if not file_name:
        print "No loaded image!"
        return
    
    processed_lines, processed_image = process_img(file_name, 1, 0)

    # convert the Image object into a TkPhoto object
    im = Image.fromarray(processed_image)
    processed_image_tk = ImageTk.PhotoImage(image=im) 

    display_image(processed_image_tk)
    
def draw_image():
    # TO DO: start drawing with robot arm
    return
    
def display_image(image):
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
filemenu.add_command(label="Open Image", command=open_image)
filemenu.add_command(label="Take Picture", command=take_picture)
filemenu.add_command(label="Process", command=process_image)
filemenu.add_command(label="Draw", command=draw_image)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Functions", menu=filemenu)

# Canvas set up
canvas = Canvas(root, width = 1920, height = 1080)

root.config(menu=menubar)
root.mainloop()


