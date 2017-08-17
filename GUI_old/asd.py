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


class SecondaryFrames(Frame):

    def __init__(self,parent):

        self.top_frame = Frame(parent)
        self.left_frame = Frame(parent, width=400)
        self.right_frame = Frame(parent, bg="green")

        self.horizontal_line = ttk.Separator(parent, orient=HORIZONTAL)
        self.vertical_line = ttk.Separator(parent, orient=VERTICAL)

class SearchFolder(Frame):

    def __init__(self,parent):
        self.parent        = parent
        self.instruction   = Label(self.parent, text='Selecione a pasta com as imagens DICOM (ainda não implementado!)')
        self.path_box      = Label(self.parent, text='Diretório: ', relief=RIDGE)
        self.search_button = Button(self.parent, text="Buscar pasta", command=self.get_images) #se colocar search_folder() - com () - ele chama a função automaticamente!
        self.dirname = ''

        self.slice_and_echo = np.ones([2,2])
        self.dcm_folder = ''
        self.dcm_files = []

    # def search_folder(self):

        # return self.dirname

    # self.diretorio = self.dirname

    def atoi(self,text):
        return int(text) if text.isdigit() else text

    def natural_keys(self,text):
        '''
        alist.sort(key=natural_keys) sorts in human order
        http://nedbatchelder.com/blog/200712/human_sorting.html
        (See Toothy's implementation in the comments)
        '''
        return [self.atoi(c) for c in re.split('(\d+)', text)]

    def get_images(self):

        # self.dirname = filedialog.askdirectory(parent=root, initialdir="/", title='Please select a directory')

        self.dirname = '/Users/yurir.tonin/Dropbox/TCC/DICOM/Dados/PAC001/601_AXI_OUT_IN PHASE 6 ECOS_PRJ1515_QD/DICOM'

        self.path_box.configure(text='Diretório: {0:s}'.format(self.dirname))
        self.dcm_folder = self.dirname         # Folder with dcm files
        self.dcm_files = [f for f in listdir(self.dcm_folder) if isfile(join(self.dcm_folder, f))]  # create list with file names
        self.dcm_files.sort(key=self.natural_keys)  # order files by their number

        # Declare empty arrays to import parameters later
        slice_thickness = np.zeros(len(self.dcm_files))
        echo_time = np.zeros(len(self.dcm_files))
        slice_number = np.zeros(len(self.dcm_files))

        # Read parameters from all files and store them in their respective arrays
        for i in range(len(self.dcm_files)):
            file_path = os.path.join(self.dcm_folder, self.dcm_files[i])

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

        # Create 2 column matrix with slice number and echo time values
        self.slice_and_echo = (np.column_stack((slice_number, echo_time)))
        echo_time_values = list(set(sorted(echo_time)))  # sorted list for echo time
        slice_number_values = list(set(sorted(slice_number)))  # sorted list for slice number

        # return self.slice_and_echo, self.dcm_folder, self.dcm_files

class Scales(Frame):

    def __init__(self,parent,label_text,initial_value,final_value):
        # Frame.__init__(self, parent)
        # super(Scales, self).__init__()
        self.parent        = parent
        self.bar_length    = 200
        self.label_text    = label_text
        self.initial_value = initial_value
        self.final_value   = final_value
        self.variable_name = DoubleVar()

        self.scale_name = Scale(self.parent, variable=self.variable_name, orient=HORIZONTAL, from_=self.initial_value, to=self.final_value,
                                length=self.bar_length, cursor="hand", label=self.label_text)

        def get_scale_value(self):
            self.variable_name.get()

class InteractiveCanvas(Frame):

    def __init__(self,parent):
        Frame.__init__(self,parent)
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

        self.coordenadas = self.canvas.coords(self.rect)
        print(self.coordenadas)
        # return self.coordenadas

    def on_button_release(self, event):
        pass

    def get_ROI(self):
        pass
        # print(self.coordenadas)
        # coord_x0 = self.coordenadas[0]
        # x_init.config(text='{0:.0f}'.format(coord_x0))

        # print(Program().dcm_all_echoes)

    def change_image(self, user_slice_number,user_echo_time,slice_and_echo,dcm_folder,dcm_files):  # WHAT IS *ARGS?

        # user_slice_number = np.float(Scales().slice_number.get())
        # user_echo_time = np.int(Scales().echo_time.get())

        echo_time_values = np.array(np.unique(slice_and_echo[:, 1]))
        # Scales().echo_value_display.configure(text=echo_time_values[user_echo_time])


        user_echo_time = echo_time_values[user_echo_time]

        # print('Echo Time : {0:.3f}          Slice Number : {1:.0f}\n'.format(np.float(user_echo_time),np.float(slice_number.get()))

        indexes = np.where(slice_and_echo[:, 0] == user_slice_number)[0]  # indexes of the elements where the user input match the element

        self.dcm_all_echoes = []
        for i in indexes:  # Go through index values. Check and record those in which echo time (element) matches user input

            #get array of arrays with pixel values for all echoes of a slice
            file_path = os.path.join(dcm_folder, dcm_files[i]) # path of the file whose index match user input
            dcm_read = dicom.read_file(file_path)  # read file user wants
            self.dcm_all_echoes.append(dcm_read.pixel_array)  # extract pixel values


            if slice_and_echo[i, 1] == user_echo_time: #Find index for specific echo_time
                selected_echo_time = user_echo_time
                selected_slice_number = slice_and_echo[i, 0]
                index = i

        file_path = os.path.join(dcm_folder, dcm_files[index])  # path of the file whose index match user input
        dcm_read = dicom.read_file(file_path)  # read file user wants
        dcm_pixel_values = dcm_read.pixel_array  # extract pixel values
        dcm_image = Image.fromarray(dcm_pixel_values).resize((300, 300))  # convert array to image #CHECAR: A SELEÇÃO VAI SER NA IMAGEM ORIGINAL OU RESIZED? PODE SER QUE A MÉDIA MUDE CASO SEJA FEITA EM UMA OU EM OUTRA!
        new_tk_image = ImageTk.PhotoImage(dcm_image)  # crete tk image

        imagem = Label(left_frame, image='')  # Create empty image to keep a reference of image. That way, GarbageCollector won't throw away image (http://effbot.org/pyfaq/why-do-my-tkinter-images-not-place_interactive_canvasear.htm)
        imagem.configure(image=new_tk_image)  # Used to keep reference (go to imagem declaration to understand)
        imagem.image = new_tk_image           # Used to keep reference (go to imagem declaration to understand)
        place_interactive_canvas.canvas.itemconfig(place_interactive_canvas.image_on_canvas, image=new_tk_image)  # update image on canvas


class MainApplication(Frame):
    def __init__(self, master):#, *args, **kwargs):
        Frame.__init__(self, master)#, *args, **kwargs)

        self.parent = master # Master will be the parent for widgets to come

# Create objects (create widgets) #

        self.secondary_frames      = SecondaryFrames(self.parent)

        self.search_folder_objects = SearchFolder(self.secondary_frames.top_frame)

        self.slice_number_scale = Scales(self.secondary_frames.left_frame,"Slice Number",1,24)
        self.echo_time_scale    = Scales(self.secondary_frames.left_frame,"Echo Time",0,5)         # echos = np.array(np.unique(slice_and_echo[:, 1]))  # Create array removing repeated values from echo array and reordering them

        self.interactive_canvas = InteractiveCanvas(self.secondary_frames.left_frame)



# Pack Frames #

        self.secondary_frames.top_frame.pack(padx=5, pady=5, side=TOP, fill=X)
        self.secondary_frames.horizontal_line.pack(side=TOP, fill=X)
        self.secondary_frames.left_frame.pack_propagate(0)
        self.secondary_frames.left_frame.pack(padx=5, pady=5, side=LEFT, fill=Y)
        self.secondary_frames.vertical_line.pack(side=LEFT, fill=Y)
        self.secondary_frames.right_frame.pack(padx=5, pady=5, fill=BOTH)

# Pack Widgets #


        self.search_folder_objects.instruction.pack(padx=2, pady=5, anchor="w")
        self.search_folder_objects.path_box.pack(padx=2, pady=1, anchor="w")
        self.search_folder_objects.search_button.pack(padx=2, pady=1, anchor="w")

        self.slice_number_scale.scale_name.pack()
        self.echo_time_scale.scale_name.pack()

        # def get_scale_var(self,object):

        print(self.search_folder_objects.slice_and_echo)

        # self.slice_number_scale.variable_name.trace("w", self.interactive_canvas.change_image(self.slice_number_scale.scale_name.get(),self.echo_time_scale.scale_name.get(),self.search_folder_objects.slice_and_echo,self.search_folder_objects.dcm_folder,self.search_folder_objects.dcm_files))
        # self.echo_time_scale.variable_name.trace("w", self.interactive_canvas.change_image(self.slice_number_scale.scale_name.get(),self.echo_time_scale.scale_name.get(),self.search_folder_objects.slice_and_echo,self.search_folder_objects.dcm_folder,self.search_folder_objects.dcm_files))))

if __name__ == '__main__':
    root = Tk()
    root.geometry("800x600")
    MainApplication(root)
    root.mainloop()
