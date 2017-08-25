


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
# from scipy import optimize
from lmfit import minimize, Parameters # lmfit is the package for fitting

# ATTENTION: This program was first implemented for an analysis of slice numbers and echo times. Only later it was
# switched to analyze slice number and flip angle. Therefore, lost of arrays and variables that coitain "echo" in their
# names posses FLIP ANGLE values, and NOT ECHO TIME values.

class SecondaryFrames(Frame):

    # This classes declares frames to divide de main window in regions for different widgets

    def __init__(self,parent):

        self.top_frame = Frame(parent)
        self.left_frame = Frame(parent, width=400)
        self.right_frame = Frame(parent, width=500)#, bg="green")
        self.right_frame2 = Frame(parent)

        self.horizontal_line = ttk.Separator(parent, orient=HORIZONTAL)
        self.vertical_line = ttk.Separator(parent, orient=VERTICAL)

class SearchFolder(Frame):

# This class is responsible for selecting the folders where acquistion files area and, after that is done, placing the
# scales and canvas used for selecting a specific image and drawing a region of interest (ROI) on it. The last action
# performed by this class is to select the ROI through a button, so that data is exported to a plot.

    def __init__(self,parent,left_frame,right_frame,right_frame2,first_run,first_plot):

        self.first_run     = first_run
        self.first_plot    = first_plot
        self.parent        = parent
        self.left_frame    = left_frame
        self.right_frame   = right_frame
        self.right_frame2  = right_frame2

        self.entry_frame = Frame(self.parent)
        self.label_acquisition  = Label(self.entry_frame,text= '(insira na caixa o número de aquisições a serem importadas na análise)')
        self.acquisition_number = IntVar()
        self.acquisition_number = Entry(self.entry_frame,width=11,justify=CENTER)
        self.acquisition_number.delete(0,END)
        self.acquisition_number.insert(0,'2')
        self.acquisition_number.pack(padx=2, pady=1, anchor="w",side=LEFT)
        self.label_acquisition.pack(padx=2, pady=1, anchor="w",side=LEFT)


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


        # self.dirname           = []
        self.dcm_folder        = []
        self.dcm_files         = []
        self.slice_thickness   = []
        self.echo_time         = []
        self.repetition_time   = []
        self.gradient_echo_train_length = []
        self.slice_number      = []
        self.flip_angle        = []
        self.rescale_intercept = []
        self.rescale_slope     = []
        self.slice_and_echo    = np.array([],dtype=np.int64).reshape(0,2)
        self.slice_and_flip    = []
        self.FOVx = []
        self.FOVy = []

        for j in range(0,np.int(self.acquisition_number.get())):
            pass

            if self.first_run == False:
            # Destroys all widgets inside of self.left_frame if this is not the first time the widget is being created.
            # This is done so that the widget can be "refreshed" without a new one appearing on the screen
                for child in self.left_frame.winfo_children():
                    child.destroy()

            if j == 0:
            # A conditional for selecting all the folders. This is only needed if you want to declare by hand
            # the folder with the dicom files. If you want the interface to search the folder to appear when you click
            # the "Search Folder" button, simply remove this conditional leaving only the command  self.dirname.append(filedialog.askdirectory(parent=root, initialdir="/", title='Selecione uma pasta'))
                # self.dirname.append(filedialog.askdirectory(parent=root, initialdir="/", title='Selecione uma pasta'))
                # self.dirname = '/Users/yurir.tonin/Dropbox/TCC/DICOM/Dados/PAC001/901_AXI FLIP 2/DICOM'
                self.dirname = 'C:/Users/Yuri Tonin/Desktop/Dados/PAC001/2901_AXI FLIP 2/DICOM'
            else:
                # self.dirname.append(filedialog.askdirectory(parent=root, initialdir="/", title='Selecione uma pasta'))
                # self.dirname = '/Users/yurir.tonin/Dropbox/TCC/DICOM/Dados/PAC001/1001_AXI FLIP 10/DICOM'
                self.dirname = 'C:/Users/Yuri Tonin/Desktop/Dados/PAC001/3001_AXI FLIP 10/DICOM'

            self.path_box.configure(text='Diretório: {0:s}'.format(self.dirname)) #Changes the name of the label to show the last selected folder
            self.dcm_folder.append(self.dirname) # Saves the folder path with dcm files to a list

            self.dcm_files.append( [f for f in listdir(self.dcm_folder[j]) if isfile(join(self.dcm_folder[j], f))]) # create list with the names of the files in the current selected folder
            self.dcm_files[j].sort(key=self.natural_keys)  # order files by their number in file name

            # Declare empty arrays to import parameters later
            self.slice_thickness.append(np.zeros(len(self.dcm_files[j])))
            self.echo_time.append(np.zeros(len(self.dcm_files[j])))
            self.repetition_time.append(np.zeros(len(self.dcm_files[j])))
            self.gradient_echo_train_length.append(np.zeros(len(self.dcm_files[j])))
            self.slice_number.append( np.zeros(len(self.dcm_files[j])))
            self.rescale_slope.append(np.zeros(len(self.dcm_files[j])))
            self.rescale_intercept.append( np.zeros(len(self.dcm_files[j])))
            self.flip_angle.append( np.zeros(len(self.dcm_files[j])))

            # Read parameters from all files and store them in their respective arrays
            for i in range(len(self.dcm_files[j])):
                file_path = os.path.join(self.dcm_folder[j], self.dcm_files[j][i])

                # ==============================================================================
                # Read file and tags
                # ==============================================================================
                dcm_read = dicom.read_file(file_path)

                self.slice_number[j][i]    = dcm_read[0x2001, 0x100A].value
                self.slice_thickness[j][i] = dcm_read[0x18, 0x50].value
                self.echo_time[j][i]       = dcm_read[0x18, 0x81].value

                self.rescale_intercept[j][i]  = dcm_read[0x28, 0x1052].value
                self.rescale_slope[j][i]      = dcm_read[0x28, 0x1053].value

                self.repetition_time[j][i]            = dcm_read[0x18,0x80].value
                self.gradient_echo_train_length[j][i] = dcm_read[0x18,0x91].value
                # magnetic_field_strength = dcm_read[0x18,0x87].value
                # gradient                = dcm_read[0x18,0x1318].value #dB/dt
                self.flip_angle[j][i]    =  dcm_read[0x18, 0x1314].value

                # Single value for all measurements
                self.rows          = dcm_read[0x28, 0x10].value
                self.columns       = dcm_read[0x28, 0x11].value
                self.pixel_spacing = dcm_read[0x28, 0x30].value



            self.slice_and_flip.append(np.column_stack((self.slice_number[j][:], self.flip_angle[j][:])))

            self.FOVx.append(self.rows * self.pixel_spacing)
            self.FOVy.append(self.columns * self.pixel_spacing)

            self.slice_and_echo = np.vstack([self.slice_and_echo,self.slice_and_flip[j]])  #THE NAME "SLICE AND ECHO" IS NOT SUITABLE! IT SHOULD ACTUALLY BE SLICE AND FLIP. MANTAINED IT LIKE THIS BECAUSE OF OLDER IMPLEMENTATION WAS CREATED FOR ECHO TIMES!

        print(dcm_read.dir())  # All Dicom tag available

        print('Echo Train Length = {0:.0f}'.format(self.gradient_echo_train_length[0][0]))
        self.total_repetition_time = np.multiply(self.repetition_time,self.gradient_echo_train_length)
        # print(self.total_repetition_time)

        self.TE = self.echo_time[0][0]*10**-3  # Value in seconds. Echo time should be the same for all elements of
                                               # the array if we are dealing with the case for different flip angles
        self.TR = self.total_repetition_time[0][0]*10**-3 # Values here work just like for echo time
        self.T1 = 678*10**-3                              # Value in seconds. T1 and T2 values are for 1.5 T
        self.T2 = 72*10**-3                               # Obtained from https://www.ncbi.nlm.nih.gov/pubmed/22302503


        self.Ernst_angle = np.arccos(np.exp(-1*self.TR/self.T1))*180/np.pi  #678ms obtained in literature for healthy liver

        print('Echo time       = {0:.2e} seconds'.format(self.TE))
        print('Repetition time = {0:.2e} seconds'.format(self.TR))
        print('Ernst angle     = {0:.1f} Degrees'.format(self.Ernst_angle))

        self.dcm_files = [item for sublist in self.dcm_files for item in sublist] # Makes a flat list (remove separation of interior lists, creating one huge list)

        self.unique_sorted_echoes = np.array(np.unique(self.slice_and_echo[:,1])) #Removing repetitions and ordering values
        self.unique_sorted_slices = np.array(np.unique(self.slice_and_echo[:,0])) #Removing repetitions and ordering values

        self.place_scales_and_canvas() # Puts everything on canvas

        self.first_run = False         # Declares that the first run has already been completed

    def place_scales_and_canvas(self):

        # Creating scale objects from the class
        self.slice_number_scale = Scales(self.left_frame,"Slice Number",self.unique_sorted_slices[0],self.unique_sorted_slices[-1])
        self.echo_time_scale    = Scales(self.left_frame,"Flip angle",0,self.unique_sorted_echoes.size-1)

        #Creating interactive canvas object where images are shown and ROI selected
        self.interactive_canvas = InteractiveCanvas(self.left_frame)

        self.slice_number_scale.scales_frame.pack(anchor='w')
        self.echo_time_scale.scales_frame.pack(anchor='w')

        self.interactive_canvas.pack(pady=15)

        self.slice_number_scale.variable_name.trace("w", self.call_change_image) #When scale is changed, calls self.call_change_image
        self.echo_time_scale.variable_name.trace("w", self.call_change_image)

        # Creates plot object to visualize data and fitting
        self.plot = Plot(self.slice_and_echo,self.first_plot,self.right_frame,self.right_frame2,self.TE,self.T1,self.T2,self.TR)

        # Creates button to select ROI after it is drawed.
        self.select_button = Button(self.left_frame,text='Selecionar região',
                                    command= lambda: self.plot.ROI_average(self.dcm_all_echoes,self.interactive_canvas.get_ROI(),self.echo_time_scale.scale_name.get(),self.slice_number_scale.scale_name.get()) )

        self.select_button.pack()

    def call_change_image(self,*args): #need *args to take arguments that are automatically passed by the tracing mechanism

    # Obtains the scale value to that this values can be passed to the interactive_canvas class, where they will be used
    # for the displayed image to be changed to an image corresponding to the new values

        self.scale1_value   = self.slice_number_scale.scale_name.get()
        self.scale2_value   = self.echo_time_scale.scale_name.get()

        self.scale1_label   = self.slice_number_scale.scale_label
        self.scale2_label = self.echo_time_scale.scale_label

        self.dcm_all_echoes = self.interactive_canvas.change_image( self.scale1_value,
                                                                    self.scale2_value,
                                                                    self.scale1_label,
                                                                    self.scale2_label,
                                                                    self.slice_and_echo,
                                                                    self.dcm_folder,
                                                                    self.dcm_files,
                                                                    self.left_frame,
                                                                    self.interactive_canvas,
                                                                    self.rescale_intercept,
                                                                    self.rescale_slope
                                                                    )

class Scales(Frame):

# This class simply declares the characteristics of the Scales used for selecting images. They are declared here, but
# only created (packed) in the GUI at SearchFolder class, inside of place_scales_and_canvas method.

    def __init__(self,parent,label_text,initial_value,final_value,*args):
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
                                cursor="hand2",
                                label=self.label_text,
                                showvalue=0)

        self.scale_label = Label(self.scales_frame)#,textvariable=self.variable_name)

        self.scale_name.grid(row=0,column=0,padx=40)
        self.scale_label.grid(row=0, column=1,padx=5)


        def get_scale_value(self):
            self.variable_name.get()

class InteractiveCanvas(Frame):

# In this class all the functionality for displaying the proper image on canvas and drawing the ROI on top of the imaged
# is created. There is also a function that returns the ROI coordinates.

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
            self.rect = self.canvas.create_rectangle(self.x, self.y, 1, 1, outline='yellow')

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

    def on_button_release(self, event):
        pass

    def change_image(self, user_slice_number,user_echo_time,scale1_label,scale2_label,slice_and_echo,dcm_folder,dcm_files,left_frame,interactive_canvas,rescale_intercept,rescale_slope):

        scale1_label.configure(text=user_slice_number) # Displays value of the slice number

        self.unique_sorted_echoes = np.array(np.unique(slice_and_echo[:,1]))
        scale2_label.configure(text=self.unique_sorted_echoes[user_echo_time]) # Displays value of the flip angle

        self.user_echo_time_index = user_echo_time # Declares the value from the scale (that may note have tha same numerical value as the echo) as an index
        user_echo_time = self.unique_sorted_echoes[self.user_echo_time_index] #Selects echo time from the array of echo time values according to the index declared above

        indexes = np.where(slice_and_echo[:, 0] == user_slice_number)[0]  # indexes of the elements where the user input match the slice number

        self.dcm_all_echoes = []

        for i in indexes:  # Go through index values. Check and record those in which echo time (element) matches user input

            #get array of arrays with pixel values for all echoes of a slice

            for n in range(len(dcm_folder)): #the range of elements of dcm_folder should match the number of different flip angles/echo times
                # Will evaluate if the i_th file dcm_files[i] exists for the folder we have.
                # It will match for 1 folder only. When it does, isfile returns True, and we
                # record the pixel array for that flip_angle/echo_time in dcm_all_echoes
                file_path = os.path.join(dcm_folder[n], dcm_files[i]) # path of the file whose index match user input
                if os.path.isfile(file_path):
                    dcm_read = dicom.read_file(file_path)  # read file user wants
                    dcm_pixels = (dcm_read.pixel_array - rescale_intercept[self.user_echo_time_index][0]) / rescale_slope[self.user_echo_time_index][0]
                    # dcm_pixels = dcm_pixels/np.max(dcm_pixels)
                    # dcm_pixels = dcm_read.pixel_array
                    self.dcm_all_echoes.append(dcm_pixels)  # extract pixel values


            if slice_and_echo[i, 1] == user_echo_time: index = i #Finds index for specific echo_time


        file_path = os.path.join(dcm_folder[self.user_echo_time_index], dcm_files[index])  # path of the file whose index match user input
        dcm_read = dicom.read_file(file_path)  # read file user wants

        dcm_pixels = dcm_read.pixel_array      #NOT USING RESCALE HERE BECAUSE THIS IS USED FOR USER VISUALIZATION ONLY. Rescaling is done only in the previous for loop, since that data is the one used for plotting/fitting
        dcm_pixel_values = dcm_pixels  # extract pixel values
        dcm_image = Image.fromarray(dcm_pixel_values).resize((300, 300))  # Convert array to image #CHECAR: A SELEÇÃO VAI SER NA IMAGEM ORIGINAL OU RESIZED? PODE SER QUE A MÉDIA MUDE CASO SEJA FEITA EM UMA OU EM OUTRA!
        new_tk_image = ImageTk.PhotoImage(dcm_image)  # crete tk image

        imagem = Label(left_frame, image='')  # Create empty image to keep a reference of image. That way, GarbageCollector won't throw away image (http://effbot.org/pyfaq/why-do-my-tkinter-images-not-place_interactive_canvasear.htm)
        imagem.configure(image=new_tk_image)  # Used to keep reference (go to imagem declaration to understand)
        imagem.image = new_tk_image           # Used to keep reference (go to imagem declaration to understand)
        interactive_canvas.canvas.itemconfig(interactive_canvas.image_on_canvas, image=new_tk_image)  # update image on canvas

        return self.dcm_all_echoes

    def get_ROI(self):
        return self.coordenadas

class Plot():

    # Creates the plot. Calculates average of each ROI and performs fitting algorithm

    def __init__(self,slice_and_echo,first_plot,right_frame,right_frame2,TE,T1,T2,TR):

        self.slice_and_echo = slice_and_echo
        self.first_plot     = first_plot
        self.right_frame    = right_frame
        self.right_frame2   = right_frame2

        self.slices_list      = []
        self.amplitudes_list  = []
        # self.decay_coefs_list = []
        self.T1_list = []

        self.TE = TE
        self.TR = TR
        # self.T1 = T1
        self.T2 = T2

    def ROI_average(self,dcm_all_echoes,coordinates,echo_time_scale_value,slice_scale_value):

        self.dcm_all_echoes = dcm_all_echoes
        self.coordinates = coordinates
        self.echo_time_scale_value = echo_time_scale_value
        self.slice_scale_value = slice_scale_value

        self.average = np.empty(len(self.dcm_all_echoes))

        for i in range(len(self.dcm_all_echoes)):

            #Calculates the average of the ROI for each echo_time/flip_angle with that slice number

            dcm_image = Image.fromarray(self.dcm_all_echoes[i]).resize((300, 300)) #CAREFUL. SIZE OF THE OPENED IMAGE MUST BE THE SAME AND THE
                                                                                   #AS THE ONE IN THE GUI BECAUSE COORDINATES ARE GIVEN IN THE GUI IMAGE
            croped_dcm_image = dcm_image.crop(coordinates)
            croped_pixel_array = np.array(croped_dcm_image)
            # croped_pixel_array = croped_pixel_array/np.max(croped_pixel_array) #normalize
            self.average[i] = np.average(croped_pixel_array)

        self.echoes = np.array(np.unique(self.slice_and_echo[:,1]))
        self.create_plot()


    def residual(self,params, x, data):
        # Parameters to be fitted must be declared below
        amplitude = params['amplitude']
        T1 = params['T1']
        # T2 = params['T2']

        model = self.model_equation(amplitude,self.TE,self.TR,T1,self.T2,x)

        return (data - model)

    def model_equation(self,a,TE,TR,T1,T2,x): # x is the flip angle
        #This is the equation to be fitted. If you change input parameters, remember to also change them when this method is called
        E1 = np.exp(-TR/T1)
        # return a*np.sin(x)*(1-E1)*np.exp(-TE/T2)/(1-E1*np.cos(x))
        return a*x/(1+0.5*E1*x**2/(1-E1)) #approximation for flip angle << Ernst angle

    def create_plot(self):

        if self.first_plot == False:
            self.the_plot.clear()
        else:
            self.plot_figure = Figure(figsize=(10, 10), dpi=100)
            self.the_plot = self.plot_figure.add_subplot(111)

        self.the_plot.plot(self.echoes,self.average,'ro')
        self.the_plot.get_yaxis().set_major_formatter(plt.LogFormatter(10, labelOnlyBase=False))

        params = Parameters()
        params.add('amplitude', value=1) #value is the initial value for fitting
        params.add('T1', value = 0.5)

        fitting = minimize(self.residual, params, args=(self.echoes, self.average))

        self.fitted_amplitude = fitting.params['amplitude'].value
        self.fitted_T1 = fitting.params['T1'].value
        # self.T2 = fitting.params['T2'].value

        if fitting.success: self.save_fit_params() # if fitting is succesfull, save the parrameters

        self.fit_x_points = np.linspace(self.echoes[0],self.echoes[-1],1000)

        self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)

        self.the_plot.plot(self.fit_x_points,self.fitted_plot)

        # self.the_plot.set_title('ROI average X Echo Time')
        self.the_plot.set_xlabel('Ângulo de Flip')
        self.the_plot.set_ylabel('Média da ROI')

        if self.first_plot == False:
            self.canvas.draw()
        else:
            self.canvas = FigureCanvasTkAgg(self.plot_figure, self.right_frame)
            self.canvas.show()
            self.canvas.get_tk_widget().pack()

        self.first_plot = False


    def save_fit_params(self):

        #Save fit params and shows them at a table

        for i in range(len(self.slices_list)): # Guarantees that only 1 line per slice number fit will appear at the table
            if self.slices_list[i] == self.slice_scale_value:
                self.repetition_message = "Você refez o fitting de um slice. A ocorrência anterior foi apagada."
                print(self.repetition_message)
                del self.slices_list[i]; del self.T1_list[i]; del self.amplitudes_list[i] #deletes the previous occurence of that slice number in the list
                break
                
        self.slices_list.append(self.slice_scale_value)
        self.T1_list.append(self.fitted_T1)
        self.amplitudes_list.append(self.fitted_amplitude)

        self.table_values = np.column_stack((self.slices_list,self.amplitudes_list,self.T1_list)) # Create a matrix with 3 columns, each column being one of the lists declared above
        self.table_values = self.table_values[np.lexsort((self.table_values[:, 0],))] #sort by 1st column keeping respective 2nd and 3rd columns

        self.table_shape = self.table_values.shape

        if self.first_plot == False: #Destroys previous table and create a new one with refreshed values
            for child in self.right_frame2.winfo_children():  # destroys all widgets inside of self.right_frame2
                child.destroy()

        t = SimpleTable(self.right_frame2, len(self.slices_list)+1 ,3)
        t.pack(side="top", fill="x")
        t.set(0,0,"Slice");         t.set(0,1,"Amplitude");         t.set(0,2,"T1")

        for m in range(self.table_shape[0]):
            for n in range(self.table_shape[1]):
                if n == 0: # This conditional is used only for the formating of the first column numbers to be different from the formating of the other columns
                    t.set(m+1, n, '{0:.0f}'.format(self.table_values[m][n]))
                else:
                    t.set(m+1,n,'{0:.2e}'.format(self.table_values[m][n]))

class SimpleTable(Frame):

    #Simply formats a table to display fit parameters values.

    def __init__(self, parent, rows=2, columns=2):
        # use black background so it "peeks through" to
        # form grid lines
        Frame.__init__(self, parent, background="black")
        self._widgets = []
        for row in range(rows):
            current_row = []
            for column in range(columns):
                label = Label(self, text="%s/%s" % (row, column),
                                 borderwidth=0, width=10)
                label.grid(row=row, column=column, sticky="nsew", padx=1, pady=1)
                current_row.append(label)
            self._widgets.append(current_row)

        for column in range(columns):
            self.grid_columnconfigure(column, weight=1)


    def set(self, row, column, value):
        widget = self._widgets[row][column]
        widget.configure(text=value)

class MainApplication(Frame):

    # This is the main application that contains the core of the program. Places secondary frames and the
    # search folder objects that are used to initialize the rest of the program

    def __init__(self, master):#, *args, **kwargs):
        Frame.__init__(self, master)#, *args, **kwargs)

        self.parent = master # Master will be the parent for widgets to come

        # print(Tk().eval('info patchlevel'))

        self.first_run = True
        self.first_plot = True

        self.secondary_frames  = SecondaryFrames(self.parent)

        self.top_frame       = self.secondary_frames.top_frame
        self.left_frame      = self.secondary_frames.left_frame
        self.right_frame     = self.secondary_frames.right_frame
        self.right_frame2    = self.secondary_frames.right_frame2


        self.secondary_frames.top_frame.pack(padx=5, pady=5, side=TOP, fill=X)
        self.secondary_frames.horizontal_line.pack(side=TOP, fill=X)
        self.secondary_frames.left_frame.pack_propagate(0)
        self.secondary_frames.left_frame.pack(padx=5, pady=5, side=LEFT, fill=Y)
        self.secondary_frames.vertical_line.pack(side=LEFT, fill=Y)
        self.secondary_frames.right_frame.pack_propagate(0)
        self.secondary_frames.right_frame.pack(padx=5, pady=5, side=LEFT, fill=Y)
        self.secondary_frames.vertical_line.pack(side=LEFT, fill=Y)
        self.secondary_frames.right_frame2.pack(padx=5, pady=20,side=LEFT, fill=Y)


        self.search_folder_objects = SearchFolder(self.top_frame,self.left_frame,self.right_frame,self.right_frame2,self.first_run,self.first_plot)

        self.search_folder_objects.entry_frame.pack(anchor='w')

        self.search_folder_objects.search_button.pack(padx=2, pady=1, anchor="w",side=LEFT)
        self.search_folder_objects.path_box.pack(padx=2, pady=1, side=LEFT)

if __name__ == '__main__':
    root = Tk()
    root.geometry("1150x530")
    MainApplication(root)
    root.mainloop()

