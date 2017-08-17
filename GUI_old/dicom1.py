#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 17 13:59:35 2017

@author: yurir.tonin
"""
import numpy as np
import matplotlib.pyplot as plt

import dicom
import os
from os import listdir
from os.path import isfile, join

#==============================================================================
# # Code to order strings with numbers ("humar order")
#https://stackoverflow.com/questions/5967500/how-to-correctly-sort-a-string-with-a-number-inside
#==============================================================================
import re
def atoi(text):
    return int(text) if text.isdigit() else text
def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]
#==============================================================================
# 
#==============================================================================

#Folder with dcm files
dcm_folder = '/Users/yurir.tonin/Dropbox/TCC/DICOM/Dados/PAC001/601_AXI_OUT_IN PHASE 6 ECOS_PRJ1515_QD/DICOM'

dcm_files = [f for f in listdir(dcm_folder) if isfile(join(dcm_folder, f))] #create list with file names
dcm_files.sort(key=natural_keys) #order files by their number

#Declare empty arrays to import parameters later
slice_thickness = np.zeros(len(dcm_files))
echo_time       = np.zeros(len(dcm_files))
slice_number    = np.zeros(len(dcm_files))

#Read parameters from all files and store them in their respective arrays
for i in range(len(dcm_files)):
    file_path = os.path.join(dcm_folder, dcm_files[i])
    
    #==============================================================================
    # Read file and tags
    #==============================================================================
    dcm_read = dicom.read_file(file_path)
    
    slice_number[i]            = dcm_read[0x2001, 0x100A].value
    slice_thickness[i]         = dcm_read[0x18, 0x50].value
    echo_time[i]               = dcm_read[0x18,0x81].value
#    repetition_time         = dcm_read[0x18,0x80].value
#    magnetic_field_strength = dcm_read[0x18,0x87].value
#    flip_angle              = dcm_read[0x18,0x1314].value
#    gradient                = dcm_read[0x18,0x1318].value #dB/dt

    #Single value for all measurements
    rows          = dcm_read[0x28, 0x10].value
    columns       = dcm_read[0x28, 0x11].value
    pixel_spacing = dcm_read[0x28, 0x30].value
FOVx = rows*pixel_spacing
FOVy = columns*pixel_spacing
    #==============================================================================
    # 
    #==============================================================================
    
#Create 2 column matrix with slice number and echo time values
slice_and_echo = np.ndarray.tolist(np.column_stack((slice_number,echo_time)))
echo_time_values = list(set(sorted(echo_time))) #sorted list for echo time
slice_number_values = list(set(sorted(slice_number))) #sorted list for slice number

#==============================================================================
# USER INPUT OF ECHO TIME AND SLICE NUMBER
#==============================================================================
print('\nSelect slice number. Possible values are integers {0:.0f} to {1:.0f}'.format(slice_number_values[0],slice_number_values[-1]))
user_slice_number = float(input('Insert slice number: '))
while user_slice_number not in slice_number_values: #while given value doesn't match possible ones, keep asking for input
    print('\nINVALID VALUE. Please re-enter value.')
    user_slice_number = float(input('Insert slice number: '))

print('\nInsert echo time. Possible values are: ')
for i in echo_time_values: print("{0:.3f}".format(i),end='    ')
user_echo_time = float(input('\nInsert echo time: '))
while user_echo_time not in echo_time_values: #while given value doesn't match possible ones, keep asking for input
    print('\nINVALID VALUE. Please re-enter value.')
    user_echo_time = float(input('Insert echo time: '))
#==============================================================================
# 
#==============================================================================

indexes = np.where(slice_number == user_slice_number)[0] #indexes of the elements where the user input match the element

for i in indexes: #Go through index values. Check and record those in which echo time (element) matches user input
    if slice_and_echo[i][1] == user_echo_time:
        selected_echo_time = user_echo_time
        selected_slice_number = slice_and_echo[i][0]
        index = i

file_path = os.path.join(dcm_folder, dcm_files[index]) #path of the file whose index match user input
dcm_read = dicom.read_file(file_path) #read file user wants
dcm_pixel_values = dcm_read.pixel_array #extract pixel values
plt.imshow(dcm_pixel_values,cmap='gray'), plt.axis('off')    
