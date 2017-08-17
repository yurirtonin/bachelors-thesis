import matplotlib  # these 3 lines need to exist in this way, otherwise matplotlib crashes with tkinter
matplotlib.use("TkAgg") #backend of matplotlib

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg,NavigationToolbar2TkAgg
from matplotlib.figure import Figure

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
        # self.instruction   = Label(self.parent, text='Selecione a pasta com as imagens DICOM')
        self.search_button = Button(self.parent, text="Buscar pasta", command=self.get_images)  # se colocar search_folder() - com () - ele chama a função automaticamente!
        self.path_box      = Label(self.parent, text='(selecione a pasta com as imagens DICOM)', relief=FLAT)

        self.dirname = ''

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

class Scales(Frame):

    def __init__(self,parent,label_text,initial_value,final_value,*args):
        # Frame.__init__(self, parent)
        # super(Scales, self).__init__()
        self.parent        = parent
        self.bar_length    = 200
        self.label_text    = label_text
        self.initial_value = initial_value
        self.final_value   = final_value
        self.variable_name = DoubleVar()

        self.scales_frame = Frame(self.parent)

        self.scale_name = Scale(self.scales_frame,
                                variable=self.variable_name,
                                orient=HORIZONTAL,
                                from_=self.initial_value,
                                to=self.final_value,
                                length=self.bar_length,
                                cursor="hand",
                                label=self.label_text,
                                showvalue=0)

        self.scale_label = Label(self.scales_frame)#,textvariable=self.variable_name)

        self.scale_name.grid(row=0,column=0,padx=40)
        self.scale_label.grid(row=0, column=1,padx=5)

        # self.slice_number_scale.scale_name.pack(pady=10,anchor='w')#,side=LEFT)
        # self.slice_number_scale.scale_label.pack(padx=10,anchor='w')#,side=LEFT)
        # self.echo_time_scale.scale_name.pack(pady=10,anchor='w')
        # self.echo_time_scale.scale_label.pack(padx=10, anchor='w')  # ,side=LEFT)

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

        self.coordenadas = [0,0,0,0]

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
        # print(self.coordenadas)

    def on_button_release(self, event):
        pass

    def change_image(self, user_slice_number,user_echo_time,slice_and_echo,dcm_folder,dcm_files,left_frame,interactive_canvas):  # WHAT IS *ARGS?

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
        interactive_canvas.canvas.itemconfig(interactive_canvas.image_on_canvas, image=new_tk_image)  # update image on canvas
        return self.dcm_all_echoes

    def get_ROI(self):
        return self.coordenadas

# class Coordinates_Widgets(Frame):
#
#     def __init__(self,parent):
#
#         self.parent = parent
#
#         self.grid_frame = Frame(self.parent)
#
#         self.label_xi = Label(self.grid_frame,text='x_i').grid(row=0,column=0)
#         self.label_xf = Label(self.grid_frame,text='x_f').grid(row=1,column=0)
#         self.label_yi = Label(self.grid_frame,text='y_i').grid(row=2,column=0)
#         self.label_yf = Label(self.grid_frame,text='y_f').grid(row=3,column=0)
#
#         self.show_xi = Label(self.grid_frame,relief = SUNKEN).grid(row=0,column=1)
#         self.show_xf = Label(self.grid_frame,relief = SUNKEN).grid(row=1,column=1)
#         self.show_yi = Label(self.grid_frame,relief = SUNKEN).grid(row=2,column=1)
#         self.show_yf = Label(self.grid_frame,relief = SUNKEN).grid(row=3,column=1)

class MainApplication(Frame):
    def __init__(self, master):#, *args, **kwargs):
        Frame.__init__(self, master)#, *args, **kwargs)

        self.parent = master # Master will be the parent for widgets to come
        # self.dcm_all_echoes = []

        # print(Tk().eval('info patchlevel'))



# Create objects (create widgets) #

        self.secondary_frames      = SecondaryFrames(self.parent)

        self.top_frame = self.secondary_frames.top_frame
        self.left_frame = self.secondary_frames.left_frame
        self.right_frame = self.secondary_frames.right_frame

        self.secondary_frames.top_frame.pack(padx=5, pady=5, side=TOP, fill=X)
        self.secondary_frames.horizontal_line.pack(side=TOP, fill=X)
        self.secondary_frames.left_frame.pack_propagate(0)
        self.secondary_frames.left_frame.pack(padx=5, pady=5, side=LEFT, fill=Y)
        self.secondary_frames.vertical_line.pack(side=LEFT, fill=Y)
        self.secondary_frames.right_frame.pack(padx=5, pady=5, fill=BOTH)


        self.search_folder_objects = SearchFolder(self.top_frame)
        # self.search_folder_objects.instruction.pack(padx=2, pady=5, anchor="w")
        self.search_folder_objects.search_button.pack(padx=2, pady=1, anchor="w",side=LEFT)
        self.search_folder_objects.path_box.pack(padx=2, pady=1, side=LEFT)

        # self.slice_and_echo = self.search_folder_objects.slice_and_echo
        #
        # self.ordered_slices = np.array(np.unique(self.slice_and_echo[:, 0]))
        # self.ordered_echoes = np.array(np.unique(self.slice_and_echo[:, 1]))


        self.slice_number_scale = Scales(self.left_frame,"Slice Number",1,2)
        self.echo_time_scale    = Scales(self.left_frame,"Echo Time",0,1)         # echos = np.array(np.unique(slice_and_echo[:, 1]))  # Create array removing repeated values from echo array and reordering them

        self.interactive_canvas = InteractiveCanvas(self.left_frame)

        # self.coordinates_widgets = Coordinates_Widgets(self.left_frame)
# Pack Frames #



# Pack Widgets #





        # self.slice_number_scale.scale_name.pack(pady=10,anchor='w')#,side=LEFT)
        # self.slice_number_scale.scale_label.pack(padx=10,anchor='w')#,side=LEFT)
        # self.echo_time_scale.scale_name.pack(pady=10,anchor='w')
        # self.echo_time_scale.scale_label.pack(padx=10, anchor='w')  # ,side=LEFT)

        self.slice_number_scale.scales_frame.pack(anchor='w')
        self.echo_time_scale.scales_frame.pack(anchor='w')

        self.interactive_canvas.pack(pady=15)

        # self.coordinates_widgets.grid_frame.pack(side=LEFT)

        # ROI_coordinates = self.interactive_canvas.get_ROI()

        # self.coordinates_widgets.select_ROI(self.interactive_canvas.get_ROI)
        # self.coordinates_widgets.select_ROI..pack()

        self.first_run = True
        self.slice_number_scale.variable_name.trace("w", self.use_get_images_first)
        self.echo_time_scale.variable_name.trace("w", self.use_get_images_first)

        # print(self.dcm_all_echoes)

        self.first_plot = True
        self.select_button = Button(self.left_frame,text='Selecionar região',
                                    command= lambda: self.ROI_average(self.dcm_all_echoes,self.interactive_canvas.get_ROI()) )
        self.select_button.pack()


    def use_get_images_first(self,*args): #need *args to take arguments that are automatically passed by the tracing mechanism

        # This function makes sure that, when scale is changed, images will be acquired first!

        if self.first_run == True and self.search_folder_objects.dirname == '':
            self.search_folder_objects.get_images()
            self.first_run = False

        self.scale1_value   = self.slice_number_scale.scale_name.get()
        self.scale2_value   = self.echo_time_scale.scale_name.get()
        self.slice_and_echo = self.search_folder_objects.slice_and_echo
        self.dcm_folder     = self.search_folder_objects.dcm_folder
        self.dcm_files      = self.search_folder_objects.dcm_files

        # self.echo_time_scale.configure(text=self.slice_and_echo[:,1][self.variab])


        self.dcm_all_echoes = self.interactive_canvas.change_image(self.slice_number_scale.scale_name.get(),
                                                                     self.echo_time_scale.scale_name.get(),
                                                                     self.search_folder_objects.slice_and_echo,
                                                                     self.search_folder_objects.dcm_folder,
                                                                     self.search_folder_objects.dcm_files,
                                                                     self.secondary_frames.left_frame,
                                                                     self.interactive_canvas)

        # print(type(self.dcm_all_echoes))

    def ROI_average(self,dcm_all_echoes,coordinates):


        self.dcm_all_echoes = dcm_all_echoes
        self.coordinates = coordinates

        self.average = np.empty(len(self.dcm_all_echoes))

        for i in range(len(dcm_all_echoes)):
            dcm_image = Image.fromarray(dcm_all_echoes[i]).resize((300, 300)) #CAREFUL. SIZE OF THE OPENED IMAGE MUST BE THE SAME AND THE
                                                                                #AS THE ONE IN THE GUI BECAUSE COORDINATES ARE GIVEN IN THE GUI IMAGE
            croped_dcm_image = dcm_image.crop(coordinates)
            croped_pixel_array = np.array(croped_dcm_image)
            # croped_pixel_array = croped_pixel_array/np.max(croped_pixel_array) #normalize
            self.average[i] = np.average(croped_pixel_array)

        # print(type(self.slice_and_echo[:,1]))
        self.echoes = np.array(np.unique(self.slice_and_echo[:,1]))

        print(self.average)
        print(self.echoes)

        if self.first_plot == True:
            self.first_plot = False
            call = self.create_plot()
        else:
            call2 = self.refresh_plot()

    def create_plot(self):
        plot_figure = Figure(figsize=(10,10), dpi=100)
        self.the_plot = plot_figure.add_subplot(111)
        self.the_plot.plot(self.echoes,self.average,'ro')
        # self.the_plot.set_title('ROI average X Echo Time')
        self.the_plot.set_xlabel('Tempo de Echo')
        self.the_plot.set_ylabel('Média da ROI')


        self.canvas = FigureCanvasTkAgg(plot_figure,self.right_frame)
        self.canvas.show()
        self.canvas.get_tk_widget().pack()

    def refresh_plot(self):
        self.the_plot.clear()
        self.the_plot.plot(self.echoes,self.average,'ro')
        # self.the_plot.set_title('ROI average X Echo Time')
        self.the_plot.set_xlabel('Tempo de Echo')
        self.the_plot.set_ylabel('Média da ROI')

        self.canvas.draw()

if __name__ == '__main__':
    root = Tk()
    root.geometry("1000x530")
    MainApplication(root)
    root.mainloop()



# install_name_tool - change
# "/System/Library/Frameworks/Tk.framework/Versions/8.5/Tk"
# "/Users/yurir.tonin/anaconda/pkgs/tk-8.5.18-0/lib/libtk8.5.dylib"
# anaconda / lib / python3.5 / lib - dynload / _tkinter.so
#
# install_name_tool -change
# "/System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl"
# "/Users/yurir.tonin/anaconda/pkgs/tk-8.5.18-0/lib/libtcl8.5.dylib"
# anaconda/lib/python3.5/lib-dynload/_tkinter.so
#
# install_name_tool -change
# "/System/Library/Frameworks/Tk.framework/Versions/8.5/Tk"
# "/Users/yurir.tonin/anaconda/pkgs/tk-8.5.18-0/lib/libtcl8.5.dylib"
# anaconda/pkgs/python-3.5.2-0/lib/python3.5/lib-dynload/_tkinter.so
#
# install_name_tool -change
# "/System/Library/Frameworks/Tcl.framework/Versions/8.5/Tcl"
# "/Users/yurir.tonin/anaconda/pkgs/tk-8.5.18-0/lib/libtcl8.5.dylib"
# anaconda/pkgs/python-3.5.2-0/lib/python3.5/lib-dynload/_tkinter.so

# /Users/yurir.tonin/anaconda/pkgs/tk-8.5.18-0/lib/libtk8.5.dylib


