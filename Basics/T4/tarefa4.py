#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 10:20:03 2017

@author: YuriRT
"""

import numpy as np

import matplotlib.image as mplim

import matplotlib.pyplot as plt

import matplotlib.pylab as plb

from PIL import Image

# Opening original image to be transformed
img = Image.open('image.png').convert('L') #Converting to grayscale
img.save('greyscale.png') #Saving grayscale image
imagem = mplim.imread('greyscale.png')
plb.imshow(imagem,cmap='gray')
plt.axis('off'), plb.show()
size = imagem.shape 
nrows = size[0] #Recording number of rows
ncols = size[1] #Recording number of columns

#Fourier transform
FT = np.fft.fft2(imagem)
FTshift = np.fft.fftshift(FT)
FTplot = np.log10(1+np.abs(FTshift))

#Inverse Fourier transform
IFT = np.fft.ifft2(FTshift)
#IFT = np.fft.ifftshift(IFT)
IFTplot = np.log10(1+np.abs(IFT))

#Subtraction of original and inverse transform
#a = np.subtract(np.log10(1+np.abs(imagem)),IFTplot)
#plb.imshow(a, cmap='gray')
#plt.axis('off'), plb.show()

#Creating meshgrids for filters
x = np.linspace(0, 0, nrows)
y = np.linspace(0, 0, ncols)
filter1, filter2 = np.meshgrid(x, y)

#Creating filters
mask_size = 20
for i in range (1,mask_size):
    for j in range (1,mask_size):
        filter1[nrows/2 - (mask_size/2) + (i-1), ncols/2 - mask_size/2 + (j-1)] = 1       
filter2 = 1 - filter1

#Filtering 
filtering1 = np.multiply(FTshift,filter1)
filtering1_plot = np.log10(1+np.abs(filtering1))
filtering2 = np.multiply(FTshift,filter2)
filtering2_plot = np.log10(1+np.abs(filtering2))

#Inverse transform of filtered images
IFT_filtering1 = np.fft.ifft2(filtering1)
IFT_filtering1_plot = np.log10(1+np.abs(IFT_filtering1))
IFT_filtering2 = np.fft.ifft2(filtering2)
IFT_filtering2_plot = np.log10(1+np.abs(IFT_filtering2))


def plotting(image1,image2,label1,label2,filename):
    plt.subplot(121), plt.imshow(image1,cmap='gray'), plt.axis('off'), plt.title(label1)
    plt.subplot(122), plt.imshow(image2,cmap='gray'), plt.axis('on'), 
    plt.tick_params(axis='both', which='both',bottom='off', left='off',labelbottom='off', labelleft='off'), plt.title(label2),
    plt.savefig(filename, dpi=500, bbox_inches='tight'),
    plt.show()

#Plotting figures:
plotting(FTplot,IFTplot,'Transform','Inverse Transform','figura0')

plotting(filter1,filter2,'Filter 1', 'Filter 2','figura1') 

plotting(filtering1_plot,filtering2_plot,'Fourier Filter 1', 'Fourier Filter 2','figura2') 

plotting(filtering1_plot,IFT_filtering1_plot,'Filter 1', 'Filtered Image','figura3') 

plotting(filtering2_plot,IFT_filtering2_plot,'Filter 2', 'Filtered Image','figura4') 

plt.subplot(131), plt.imshow(imagem,cmap='gray'), plt.axis('off'), plt.title('Original Image')
plt.subplot(132), plt.imshow(IFT_filtering1_plot,cmap='gray'), plt.axis('off'), plt.title('Filtered Image 1')
plt.subplot(133), plt.imshow(IFT_filtering2_plot,cmap='gray'), plt.axis('on'),
plt.tick_params(axis='both', which='both',bottom='off', left='off',labelbottom='off', labelleft='off'), plt.title('Filtered Image 2'), 
plt.savefig('figuraFinal.png',dpi=500,bbox_inches='tight'),
plt.show()



















