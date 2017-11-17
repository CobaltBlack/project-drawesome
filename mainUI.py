'''
arm_control.py

"Insert some message Eric would approve here"
'''

from image_processing.image_processing import ImageProcessor
from arm_control.arm_control import ArmController

from Tkinter import *
import ttk as ttk
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
import os
import threading
import time

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080
IMAGE_DISPLAY_SIZE = 640

def open_image():
    update_status_message("Please choose an image file...")

    global file_name
    file_name = askopenfilename()

    if not file_name:
        print "Open image canceled!"
        update_status_message("Image loading canceled!")
        return

    if ip.load_image(file_name): # load in image to image processor
        display_image(Image.open(file_name))
        update_status_message("Image loaded!")
    else:
        update_status_message("Incorrect format!")

def preview_image():
    #os.system("raspistill -t 5000 -sh " + str(sharpness.get()) + " -co " + str(contrast.get()) + " -br " + str(brightness.get()) + " -sa " + str(saturation.get()) + " --ISO " + str(iso.get()))
    os.system("raspistill -t 5000")

    # test
    """
    print sharpness.get()
    print contrast.get()
    print brightness.get()
    print saturation.get()
    print iso.get()
    """

def take_picture():
    update_status_message("Image capturing...")

    pi_photo_filename = "pi_photo.jpg"
    #os.system("raspistill -o " + pi_photo_filename + " -sh " + str(sharpness.get()) + " -co " + str(contrast.get()) + " -br " + str(brightness.get()) + " -sa " + str(saturation.get()) + " --ISO " + str(iso.get()))
    os.system("raspistill -o " + pi_photo_filename)

    if ip.load_image(pi_photo_filename): # load in image to image processor
        display_image(Image.open(pi_photo_filename))
        update_status_message("Image captured!")
    else:
        update_status_message("Failed to capture image!")

def process_image():
    # check conditions
    if not ip.is_image_loaded:
        print "No loaded image!"
        update_status_message("No loaded image!")
        return

    processing = threading.Thread(target=process_image_threaded, args=[])
    processing.start()

def process_image_threaded():
    # disable buttons
    button_normal_disable()
    
    #set_cursor_wait()
    update_status_message("Image processing")
    global processing
    processing = True
    dotting = threading.Thread(target=dot_dot_dot, args=[])
    dotting.start()

    # process image
    drawing_instructions, img_shape = ip.process_image(use_shading=0)

    # load instructions to arm controller
    ac.load_instructions(drawing_instructions, img_shape)

    # convert the Image object into a TkPhoto object
    preview_processed_image = Image.fromarray(ip.get_preview_image())

    # preview
    display_image(preview_processed_image)

    #set_cursor_normal()
    processing = False
    update_status_message("Image processed!")

    # re-enable buttons
    button_normal_enable()

# nothing to see here folks
def dot_dot_dot():
    status.config(text = "Image processing")
    while (processing):
        if (processing):
            status.config(text = "Image processing")
        time.sleep(0.5)
        if (processing):
            status.config(text = "Image processing.")
        time.sleep(0.5)
        if (processing):
            status.config(text = "Image processing..")
        time.sleep(0.5)
        if (processing):
            status.config(text = "Image processing...")
        time.sleep(0.5)
        if (processing):
            status.config(text = "Image processing....")
        time.sleep(0.5)
        if (processing):
            status.config(text = "Image processing.....")
        time.sleep(0.5)

def draw_image():
    # check conditions
    if not ip.is_image_loaded:
        print "No loaded image!"
        update_status_message("No processed image!")
        return
    
    # update buttons
    button_setup_drawing()

    # draw on seperate thread
    drawing = threading.Thread(target=draw_image_threaded, args=[])
    drawing.start()

    # update progress until complete
    #progress = threading.Thread(target=update_drawing_progress_threaded, args=[])
    #progress.start()

def draw_image_threaded():
    #set_cursor_wait()
    update_status_message("Image drawing...")

    ac.testing()
    #ac.draw_loaded_instructions()

    # update buttons
    button_setup_normal()

    #set_cursor_normal()
    update_status_message("Image drawn!")
    
def update_drawing_progress_threaded():
    while (ac.get_drawing_progress() != 1):
        time.sleep(1)
        update_status_message("Image drawing... " + str(ac.get_drawing_progress()) + "%")
        print "progress bar - drawing"

    time.sleep(1)
    update_status_message("Image drawing... " + str(ac.get_drawing_progress()) + "% Drawing complete.")

def draw_image_pause():
    if (ac.draw_pause):
        button_pause.config(text="PAUSE") 
    else:
        button_pause.config(text="UNPAUSE") 
    ac.draw_image_pause()

def draw_image_abort():
    ac.draw_image_abort()

# only pass in PIL.Image objects
def display_image(image):
    # Resize to smaller fit on window
    img_w, img_h = image.size
    ratio = 1.0
    if img_h >= img_w:
        ratio = float(IMAGE_DISPLAY_SIZE) / float(img_h)
    else:
        ratio = float(IMAGE_DISPLAY_SIZE) / float(img_w)
    img_h = int(img_h * ratio)
    img_w = int(img_w * ratio)
    scaled_image = image.resize((img_w, img_h), Image.BILINEAR)

    # Convert to Tkinter.PhotoImage
    photo_img = ImageTk.PhotoImage(scaled_image)

    #root.geometry("" + str(img_w) + "x" + str(img_h+70) + "")

    canvas.delete("all")
    canvas.photo_img = photo_img
    canvas.pack()
    canvas.create_image(IMAGE_DISPLAY_SIZE/2, IMAGE_DISPLAY_SIZE/2, image=photo_img)

def update_status_message(message):
    status.config(text="")
    message = threading.Thread(target=update_status_message_threaded, args=[message])
    message.start()

def update_status_message_threaded(message):
    time.sleep(0.01)
    status.config(text=message)

def set_cursor_wait():
    root.config(cursor="starting")  # arrow + circle
    #root.config(cursor="wait")     # circle

def set_cursor_normal():
    root.config(cursor="")

# work in progress
def scale(photo_img):
    img_w = photo_img.width()
    img_h = photo_img.height()

    new_h = img_h
    new_w = img_w

    if img_w > DISPLAY_WIDTH:
        ratio = DISPLAY_WIDTH/img_w
        new_h = int(img_h * ratio)
        new_w = int(img_w * ratio)

    if new_h > DISPLAY_HEIGHT:
        ratio = DISPLAY_HEIGHT/new_h
        new_h = int(new_h * ratio)
        new_w = int(new_w * ratio)

    scale_w = new_w/img_w
    scale_h = new_h/img_h
    photo_img.zoom(int(scale_w), int(scale_h))

    return photo_img

def settings_window():
    master = Tk()
    master.title("Settings")
    master.geometry("180x350");
    Label(master, text="").pack()

    global brightness
    brightness = Scale(master, from_=0, to=100, orient=HORIZONTAL)
    brightness.set(50)
    brightness.pack() #fill=X,padx=10) # TEST TEST TEST
    Label(master, text="Brightness").pack()
    #Button(master, text='Set Brightness', command=show_value_brightness).pack()

    #master = Tk()
    global sharpness
    sharpness = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
    sharpness.set(0)
    sharpness.pack()
    Label(master, text="Sharpness").pack()
    #Button(master, text='Set Sharpness', command=show_value_sharpness).pack()

    #master = Tk()
    global contrast
    contrast = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
    contrast.set(0)
    contrast.pack()
    Label(master, text="Contrast").pack()
    #Button(master, text='Set Contrast', command=show_value_contrast).pack()

    #master = Tk()
    global saturation
    saturation = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
    saturation.set(50)
    saturation.pack()
    Label(master, text="Saturation").pack()
    #Button(master, text='Set Saturation', command=show_value_saturation).pack()

    #master = Tk()
    global iso
    iso = Scale(master, from_=0, to=200, orient=HORIZONTAL)
    iso.set(0)
    iso.pack()
    Label(master, text="ISO").pack()
    #Button(master, text='Set ISO', command=show_value_iso).pack()

def show_value_brightness():
    print ("Brightness set to: ")
    print (brightness.get())

def show_value_sharpness():
    print ("Sharpness set to: ")
    print (sharpness.get())

def show_value_contrast():
    print ("Contrast set to: ")
    print (contrast.get())

def show_value_saturation():
    print ("Saturation set to: ")
    print (saturation.get())

def show_value_iso():
    print ("ISO set to: ")
    print (iso.get())

def button_setup_normal():
    print("button_setup_normal")
    # Button bar
    global toolbar
    toolbar.destroy()

    toolbar = Frame(toolbar_parent) # toolbar = Frame(height=2, bd=1, relief=SUNKEN)
    toolbar.pack(anchor=CENTER, fill=X, padx=5, pady=5)
    # Buttons
    global button_load
    button_load = ttk.Button(toolbar, text="LOAD", width=9, command=open_image)
    button_load.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    global button_capture
    button_capture = ttk.Button(toolbar, text="CAPTURE", width=9, command=take_picture)
    button_capture.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    global button_process
    button_process = ttk.Button(toolbar, text="PROCESS", width=9, command=process_image)
    button_process.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    global button_draw
    button_draw = ttk.Button(toolbar, text="DRAW", width=9, command=draw_image)
    button_draw.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    # Pack
    toolbar.pack(side=BOTTOM, fill=X)

def button_setup_drawing():
    print("button_setup_drawing")
    # Button bar
    global toolbar
    toolbar.destroy()
    
    toolbar = Frame(toolbar_parent) # toolbar = Frame(height=2, bd=1, relief=SUNKEN)
    toolbar.pack(anchor=CENTER, fill=X, padx=5, pady=5)
    # Buttons
    global button_pause
    button_pause = ttk.Button(toolbar, text="PAUSE", width=9, command=draw_image_pause)
    button_pause.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    b = ttk.Button(toolbar, text="ABORT", width=9, command=draw_image_abort)
    b.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
    # Pack
    toolbar.pack(side=BOTTOM, fill=X)
    
def button_normal_disable():
    global button_load
    button_load.config(state=DISABLED)
    global button_capture
    button_capture.config(state=DISABLED)
    global button_process
    button_process.config(state=DISABLED)
    global button_draw
    button_draw.config(state=DISABLED)

def button_normal_enable():
    global button_load
    button_load.config(state=NORMAL)
    global button_capture
    button_capture.config(state=NORMAL)
    global button_process
    button_process.config(state=NORMAL)
    global button_draw
    button_draw.config(state=NORMAL)
    
# Set up
global root
root = Tk()
root.title("Image Processor")
root.geometry("640x700")
root.configure(background='#DCDAD5')

s = ttk.Style()
s.theme_use('clam')

# initialization
file_name = ""
ip = ImageProcessor()
ac = ArmController()

# Menu bar set up
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Preview", command=preview_image)
filemenu.add_command(label="Image Settings", command=settings_window)
filemenu.add_command(label="Debug", command=button_setup_normal)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Options", menu=filemenu)

# Status bar
status = ttk.Label(root, text="Welcome to Team Drawsome Image Processor!")#, bd = 1, relief = SUNKEN, anchor = W)
status.pack(side = BOTTOM, fill = X)

# Button bar
global toolbar_parent
toolbar_parent = Frame(root) #toolbar_parent = Frame(root, height=2, bd=1, relief=SUNKEN)
toolbar_parent.pack(anchor=CENTER, fill=X)
# Buttons
global toolbar
toolbar = Frame(toolbar_parent)
button_setup_normal()
# Pack
toolbar_parent.pack(side=BOTTOM, fill=X)

# Button bar seperator
separator = ttk.Frame(height=2)#, bd=1, relief=SUNKEN)
separator.pack(side = BOTTOM, fill = X) # separator.pack(fill=X, padx=5, pady=5)

# Canvas set up
canvas = Canvas(root, width = 1920, height = 1080)
root.config(menu=menubar)
root.mainloop()
