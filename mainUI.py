from image_processing.image_processing import process_img

from Tkinter import *
from tkFileDialog import askopenfilename
from PIL import Image
import os
brightness = 42
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

def take_picture():
    global file_name
    os.system("raspistill -o name.jpg -sh " + str(sharpness.get()) + " -co " + str(contrast.get()) + " -br " + str(brightness.get()) + " -sa " + str(saturation.get()) + " --ISO " + str(iso.get()))
    
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
root.geometry("300x300");

# Menu bar set up
menubar = Menu(root)
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Preview", command=preview_image)
filemenu.add_command(label="Open Image", command=open_image)
filemenu.add_command(label="Take Picture", command=take_picture)
filemenu.add_command(label="Process", command=process_image)
filemenu.add_command(label="Draw", command=draw_image)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Functions", menu=filemenu)

master = Tk()
brightness = Scale(master, from_=0, to=100, orient=HORIZONTAL)
brightness.set(50)
brightness.pack()
Button(master, text='Set Brightness', command=show_value_brightness).pack()

master = Tk()
sharpness = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
sharpness.set(0)
sharpness.pack()
Button(master, text='Set Sharpness', command=show_value_sharpness).pack()

master = Tk()
contrast = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
contrast.set(0)
contrast.pack()
Button(master, text='Set Contrast', command=show_value_contrast).pack()


master = Tk()
saturation = Scale(master, from_=-100, to=100, orient=HORIZONTAL)
saturation.set(50)
saturation.pack()
Button(master, text='Set Saturation', command=show_value_saturation).pack()

master = Tk()
iso = Scale(master, from_=0, to=200, orient=HORIZONTAL)
iso.set(0)
iso.pack()
Button(master, text='Set ISO', command=show_value_iso).pack()

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


# Canvas set up
canvas = Canvas(root, width = 1920, height = 1080)

root.config(menu=menubar)
root.mainloop()


