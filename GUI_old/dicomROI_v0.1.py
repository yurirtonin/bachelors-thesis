#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 13:59:35 2017

@author: Yuri Rossi Tonin
"""
import numpy as np

import matplotlib  # these 3 lines need to exist in this way, otherwise matplotlib crashes with tkinter

matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

import dicom
import os
from os import listdir
from os.path import isfile, join

from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
import numpy as np


root = Tk()
root.title("Seleção de corte e echo")
root.geometry("800x600")

top_frame = Frame(root)
left_frame = Frame(root, width=400)
right_frame = Frame(root, bg="green")

horizontal_line = ttk.Separator(root, orient=HORIZONTAL)
vertical_line = ttk.Separator(root, orient=VERTICAL)

top_frame.pack(padx=5, pady=5, side=TOP, fill=X)
horizontal_line.pack(side=TOP, fill=X)
left_frame.pack_propagate(0)
left_frame.pack(padx=5, pady=5, side=LEFT, fill=Y)
vertical_line.pack(side=LEFT, fill=Y)
right_frame.pack(padx=5, pady=5, fill=BOTH)


class Program():

    def Acquire_Dicom(self):
        def atoi(text):
            return int(text) if text.isdigit() else text

        def natural_keys(text):
            '''
            alist.sort(key=natural_keys) sorts in human order
            http://nedbatchelder.com/blog/200712/human_sorting.html
            (See Toothy's implementation in the comments)
            '''
            return [atoi(c) for c in re.split('(\d+)', text)]

        # ==============================================================================
        # ==============================================================================

        # Folder with dcm files
        dcm_folder = '/Users/yurir.tonin/Dropbox/TCC/DICOM/Dados/PAC001/601_AXI_OUT_IN PHASE 6 ECOS_PRJ1515_QD/DICOM'

        dcm_files = [f for f in listdir(dcm_folder) if isfile(join(dcm_folder, f))]  # create list with file names
        dcm_files.sort(key=natural_keys)  # order files by their number

        # Declare empty arrays to import parameters later
        slice_thickness = np.zeros(len(dcm_files))
        echo_time = np.zeros(len(dcm_files))
        slice_number = np.zeros(len(dcm_files))

        # Read parameters from all files and store them in their respective arrays
        for i in range(len(dcm_files)):
            file_path = os.path.join(dcm_folder, dcm_files[i])

            # ==============================================================================
            # Read file and tags
            # ==============================================================================
            dcm_read = dicom.read_file(file_path)

            slice_number[i] = dcm_read[0x2001, 0x100A].value
            slice_thickness[i] = dcm_read[0x18, 0x50].value
            echo_time[i] = dcm_read[0x18, 0x81].value
            #    repetition_time         = dcm_read[0x18,0x80].value
            #    magnetic_field_strength = dcm_read[0x18,0x87].value
            #    flip_angle              = dcm_read[0x18,0x1314].value
            #    gradient                = dcm_read[0x18,0x1318].value #dB/dt

            # Single value for all measurements
            rows = dcm_read[0x28, 0x10].value
            columns = dcm_read[0x28, 0x11].value
            pixel_spacing = dcm_read[0x28, 0x30].value
        FOVx = rows * pixel_spacing
        FOVy = columns * pixel_spacing
        # ==============================================================================
        #
        # ==============================================================================

        # Create 2 column matrix with slice number and echo time values
        slice_and_echo = (np.column_stack((slice_number, echo_time)))
        echo_time_values = list(set(sorted(echo_time)))  # sorted list for echo time
        slice_number_values = list(set(sorted(slice_number)))  # sorted list for slice number

        return slice_and_echo, dcm_folder, dcm_files

    def search_folder(self):
        dirname = filedialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')
        path_box.configure(text='Diretório: {0:s}'.format(dirname))

    def change_image(self, *args):  # WHAT IS *ARGS?

        user_slice_number = np.float(slice_number.get())
        user_echo_time = np.int(echo_time.get())

        echo_time_values = np.array(np.unique(slice_and_echo[:, 1]))
        echo_value_display.configure(text=echo_time_values[user_echo_time])

        user_echo_time = echo_time_values[user_echo_time]

        # print('Echo Time : {0:.3f}          Slice Number : {1:.0f}\n'.format(np.float(user_echo_time),np.float(slice_number.get()))

        indexes = np.where(slice_and_echo[:, 0] == user_slice_number)[
            0]  # indexes of the elements where the user input match the element

        for i in indexes:  # Go through index values. Check and record those in which echo time (element) matches user input
            if slice_and_echo[i, 1] == user_echo_time:
                selected_echo_time = user_echo_time
                selected_slice_number = slice_and_echo[i, 0]
                index = i

        file_path = os.path.join(dcm_folder, dcm_files[index])  # path of the file whose index match user input
        dcm_read = dicom.read_file(file_path)  # read file user wants
        dcm_pixel_values = dcm_read.pixel_array  # extract pixel values
        dcm_image = Image.fromarray(dcm_pixel_values).resize((300, 300))  # convert array to image
        new_tk_image = ImageTk.PhotoImage(dcm_image)  # crete tk image

        imagem = Label(left_frame, image='')  # Create empty image to keep a reference of image. That way, GarbageCollector won't throw away image (http://effbot.org/pyfaq/why-do-my-tkinter-images-not-appear.htm)
        imagem.configure(image=new_tk_image)  # Used to keep reference (go to imagem declaration to understand)
        imagem.image = new_tk_image           # Used to keep reference (go to imagem declaration to understand)
        app.canvas.itemconfig(app.image_on_canvas, image=new_tk_image)  # update image on canvas

class InteractiveCanvas(Frame):

    def __init__(self,master):
        Frame.__init__(self,master=left_frame)
        self.x = self.y = 0
        self.canvas = Canvas(self,width=300,height = 300,bg="red", cursor="cross")

        self.sbarv=Scrollbar(self,orient=VERTICAL)
        self.sbarh=Scrollbar(self,orient=HORIZONTAL)
        self.sbarv.config(command=self.canvas.yview)
        self.sbarh.config(command=self.canvas.xview)

        self.canvas.config(yscrollcommand=self.sbarv.set)
        self.canvas.config(xscrollcommand=self.sbarh.set)

        self.canvas.grid(row=0,column=0,sticky=N+S+E+W)
        self.sbarv.grid(row=0,column=1,stick=N+S)
        self.sbarh.grid(row=1,column=0,sticky=E+W)

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.rect = None

        self.start_x = None
        self.start_y = None

        self.im = Image.open('greyscale.png')
        self.wazil,self.lard=self.im.size
        self.canvas.config(scrollregion=(0,0,self.wazil,self.lard))
        self.tk_im = ImageTk.PhotoImage(self.im)
        self.image_on_canvas = self.canvas.create_image(0,0,anchor="nw",image=self.tk_im) #create image on canvas


    def on_button_press(self, event):
        # save mouse drag start position
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)

        # create rectangle if not yet exist
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='green')

    def on_move_press(self, event):
        curX = self.canvas.canvasx(event.x)
        curY = self.canvas.canvasy(event.y)

        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if event.x > 0.9*w:
            self.canvas.xview_scroll(1, 'units')
        elif event.x < 0.1*w:
            self.canvas.xview_scroll(-1, 'units')
        if event.y > 0.9*h:
            self.canvas.yview_scroll(1, 'units')
        elif event.y < 0.1*h:
            self.canvas.yview_scroll(-1, 'units')

        # expand rectangle as you drag the mouse
        self.canvas.coords(self.rect, self.start_x, self.start_y, curX, curY)

        coordenadas = self.canvas.coords(self.rect)
        print(coordenadas)

    def on_button_release(self, event):
        pass

class SearchFolder(Frame):
    def __init__(self,master=top_frame):
        Frame.__init__(self,master=top_frame)

        instruction = Label(top_frame, text='Selecione a pasta com as imagens DICOM (ainda não implementado!)').pack(padx=2, pady=5, anchor="w")
        path_box = Label(top_frame, text='Diretório: ', relief=RIDGE)
        path_box.pack(padx=2, pady=1, anchor="w")

        search_folder = Button(top_frame, text="Buscar pasta", command=Program().search_folder)
        search_folder.pack(padx=2, pady=1, anchor="w")

slice_and_echo, dcm_folder, dcm_files = Program().Acquire_Dicom()

place_search_folder = SearchFolder(top_frame).pack()

class Scales(Frame):
    def __init__(self, master=left_frame):
        Frame.__init__(self, master=left_frame)


# CREATING SCALES TO SELECT VALUES
bar_length = 200
slice_number = DoubleVar()
scale_slice = Scale(left_frame, variable=slice_number, orient=HORIZONTAL, from_=1, to=24, length=bar_length,
                    cursor="hand", label="Slice Number")
scale_slice.pack(anchor=CENTER)

echo_time = DoubleVar()
echos = np.array(np.unique(slice_and_echo[:, 1]))  # Create array removing repeated values from echo array and reordering them
min_echo = echos[0]
max_echo = echos[-1]
scale_echo = Scale(left_frame, variable=echo_time, orient=HORIZONTAL, from_=0, to=echos.size - 1, length=bar_length,
                   cursor="hand", label="Flip Angle", showvalue=0)
scale_echo.pack(anchor=CENTER)
echo_value_display = Label(left_frame, text='')
echo_value_display.pack()
# === # === # === # === # === # === # === # === # === # === # === # === # === # === # === # === # === # === # === # ===

app = InteractiveCanvas(left_frame)
app.pack()

# graph_file = ImageTk.PhotoImage(file="greyscale.png")
# graph = Label(right_frame, image=graph_file)
# graph.pack(anchor="s")

slice_number.trace("w", Program().change_image)  # Goes to function change_image when slicer is changed
echo_time.trace("w", Program().change_image)  # Goes to function change_image when slicer is changed



root.mainloop()