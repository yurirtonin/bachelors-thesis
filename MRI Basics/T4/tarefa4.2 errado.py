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
#plb.imshow(imagem,cmap='gray')
#plt.axis('off'), plb.show()
size = imagem.shape 
nrows = size[0] #Recording number of rows
ncols = size[1] #Recording number of columns

line = np.empty([nrows,ncols])
column = np.empty([nrows,ncols])

matrix_rows = np.empty([0,ncols])
matrix_cols = np.empty([0,nrows])

#a = [[]]
#a[0] = np.ones(5)
#a[1] = np.ones(5)
#b = [[]]

for i in range(0,nrows):
    line[i] = imagem[i,:]

    FT_row = np.fft.fft(line[i])
    FTshift_row = np.fft.fftshift(FT_row)
    FTplot_row = np.log10(1+np.abs(FTshift_row))
    
    IFT_row = np.fft.ifft(FTshift_row)
#    a[i] = IFT_row
    IFTplot_row = np.log10(1+np.abs(IFT_row))
    
    matrix_rows = np.vstack((matrix_rows,IFTplot_row))

for i in range(0,ncols):
    column[i] = imagem[:,i]

    FT_col = np.fft.fft(column[i])
    FTshift_col = np.fft.fftshift(FT_col)
    FTplot_col = np.log10(1+np.abs(np.transpose(FTshift_col)))
    
    IFT_col = np.fft.ifft(FTshift_col)
#    b[i] = IFT_col
    IFTplot_col = np.log10(1+np.abs((IFT_col)))
    
    matrix_cols = np.vstack((matrix_cols,IFTplot_col))
    
matrix_cols = np.transpose(matrix_cols)

final_matrix = np.add(matrix_rows,matrix_cols)

#matrix = np.array([[1,2,3],[4,5,6],[7,8,9]])
#
#print(matrix)
#print(matrix[0])
#print(matrix[:,0])
   


def plotting(image1,image2,label1,label2,filename):
    plt.subplot(121), plt.imshow(image1,cmap='gray'), plt.axis('off'), plt.title(label1)
    plt.subplot(122), plt.imshow(image2,cmap='gray'), plt.axis('on'), 
    plt.tick_params(axis='both', which='both',bottom='off', left='off',labelbottom='off', labelleft='off'), plt.title(label2),
    plt.savefig(filename, dpi=500, bbox_inches='tight'),
    plt.show()

#Plotting figures:
#plotting(imagem,matrix_cols,'Original','Transform Column','1DFT0')    
    
#plotting(matrix_rows,matrix_cols,'Transform Row','Transform Column','1DFT')

plotting(imagem,final_matrix,'Original','1D+1D','1DFT0')    
 
















