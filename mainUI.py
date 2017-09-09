from image_processing.image_processing import process_img

from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image, ImageTk
import os


global sharpness
global contrast
global brightness
global saturation
global iso

DISPLAY_WIDTH = 1920
DISPLAY_HEIGHT = 1080

def open_image():
    global file_name
    
    file_name = askopenfilename()
    
    if not file_name:
        print "Open image canceled!"
        return
    
    loaded_image = ImageTk.PhotoImage(Image.open(file_name))
    display_image(loaded_image)

def preview_image():     
    os.system("raspistill -t 5000 -sh " + str(sharpness.get()) + " -co " + str(contrast.get()) + " -br " + str(brightness.get()) + " -sa " + str(saturation.get()) + " --ISO " + str(iso.get()))
    print sharpness.get()
    print contrast.get()
    print brightness.get()
    print saturation.get()
    print iso.get()

def take_picture():
    global file_name
    os.system("raspistill -o name.jpg -sh " + str(sharpness.get()) + " -co " + str(contrast.get()) + " -br " + str(brightness.get()) + " -sa " + str(saturation.get()) + " --ISO " + str(iso.get()))

def process_image():
    global file_name
    
    if not file_name:
        print "No loaded image!"
        return
    
    processed_lines, processed_image = process_img(file_name, 1, 0)

    # convert the Image object into a TkPhoto object
    im = Image.fromarray(processed_image)    
    processed_photo_img = ImageTk.PhotoImage(image=im) 

    display_image(processed_photo_img)
    
def draw_image():
    # TO DO: start drawing with robot arm
    return
    
# only pass in PhotoImage
def display_image(photo_img):
    
    #photo_img = scale(photo_img)

    img_w = photo_img.width()
    img_h = photo_img.height()
    root.geometry("" + str(img_w) + "x" + str(img_h) + "")
    
    canvas.delete("all")
    canvas.photo_img = photo_img
    canvas.pack()
    canvas.create_image(0, 0, anchor = NW, image=photo_img)

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

# Set up
root = Tk()
root.title("Image Processor")
root.geometry("330x330")

# Menu bar set up
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Preview", command=preview_image)
filemenu.add_command(label="Open Image", command=open_image)
filemenu.add_command(label="Take Picture", command=take_picture)
filemenu.add_command(label="Process", command=process_image)
filemenu.add_command(label="Draw", command=draw_image)
filemenu.add_command(label="Image Settings", command=settings_window)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Functions", menu=filemenu)



# Status bar
status = Label(root, text="Loading dank memes...", bd = 1, relief = SUNKEN, anchor = W)
status.pack(side = BOTTOM, fill = X)



# Button bar
toolbar = Frame(root)
#toolbar = Frame(height=2, bd=1, relief=SUNKEN)
toolbar.pack(anchor=CENTER, fill=X, padx=5, pady=5)
# Buttons
b = Button(toolbar, text="LOAD", width=9, command=open_image)
b.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
b = Button(toolbar, text="CAPTURE", width=9, command=take_picture)
b.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
b = Button(toolbar, text="PROCESS", width=9, command=process_image)
b.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)
b = Button(toolbar, text="DRAW", width=9, command=draw_image)
b.pack(anchor=CENTER, side=LEFT, padx=2, pady=2)

toolbar.pack(side=BOTTOM, fill=X)

# Button bar
separator = Frame(height=2, bd=1, relief=SUNKEN)
separator.pack(side = BOTTOM, fill = X)
#separator.pack(fill=X, padx=5, pady=5)




"""
def second_window():
 
    subwindow = Toplevel(window)
    subwindow.title('random title')
    subwindow.configure(bg='purple')
 
    def show_values():
        print w1.get(), w2.get(), w3.get()
 
    btn_ent = Button(subwindow, text='Enter', command=timed_window)
    btn_ent.grid(row=3, column=3, padx=5, pady=5)
    label_chem = Label(subwindow, bg='purple', text='Please Choose Chemical Levels')
    label_chem.grid(row=0, column=2, padx=5, pady=5)
    label_nic = Label(subwindow, bg='purple', text='Nictonine (mg)')
    label_nic.grid(row=1, column=1, padx=5, pady=5)
    label_glyc = Label(subwindow, bg='purple', text='Glycol (mg)')
    label_glyc.grid(row=1, column=2, padx=5, pady=5)
    label_gli = Label(subwindow , bg='purple', text='Glycerine (mg)')
    label_gli.grid(row=1, column=3, padx=5, pady=5)
    w1 = Scale(subwindow, bg='purple', from_=30, to=0, orient=VERTICAL, resolution=0.5)
    w1.grid(row=2, column=1, padx=5, pady=5)
    w2 = Scale(subwindow, bg='purple', from_=30, to=0, orient=VERTICAL, resolution=0.5)
    w2.grid(row=2, column=2, padx=5, pady=5)
    w3 = Scale(subwindow, bg='purple', from_=30, to=0, orient=VERTICAL, resolution=0.5)
    w3.grid(row=2, column=3, padx=5, pady=5)

def timed_window():
    global time
 
    time = 50
 
    def countdown():
        global time
 
        if time > 0:
            time -= 1
            lab.config(text=str(time))
            subwindow.after(100, countdown) # 100 miliseconds
        else:
            subwindow.destroy()
 
    subwindow = Toplevel(window)
    subwindow.title('countdown')
    subwindow.configure(bg='purple')
 
    lab = Label(subwindow, bg='purple', text=str(time))
    lab.pack(padx=20, pady=20)
 
    subwindow.after(100, countdown) # 100 miliseconds

#-----------------------------------------------    
# mainwindow

window = Tk()
window.title('company name')
window.configure(bg='purple')
label = Label(window, text='company name with slogan')
label.grid(row=0, column=1)
btn_nxt = Button(window, bg='purple',  text='Enter', command=second_window)  
btn_nxt.grid(row=1, column=1, padx=100, pady=100)
"""

# Canvas set up
canvas = Canvas(root, width = 1920, height = 1080)

root.config(menu=menubar)
root.mainloop()


