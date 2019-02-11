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
img = Image.open('image50.png').convert('L') #Converting to grayscale
img.save('greyscale.png') #Saving grayscale image
imagem = mplim.imread('greyscale.png')
#plb.imshow(imagem,cmap='gray')
#plt.axis('off'), plb.show()
size = imagem.shape 
nrows = size[0] #Recording number of rows
ncols = size[1] #Recording number of columns

# 2D Fourier transform
FT = np.fft.fft2(imagem)
FTshift = np.fft.fftshift(FT)
FTplot = np.log10(1+np.abs(FTshift))
#FTplot = np.log10(1+np.abs(FT))

# 2D Inverse Fourier transform
IFT = np.fft.ifft2(FTshift)
#IFT = np.fft.ifftshift(IFT)
IFTplot = np.log10(1+np.abs(IFT))



#Declarations for 1D transforms (row-wise and column-wise)
line = np.empty([nrows,ncols])
FT_row = np.empty([nrows,ncols],dtype=complex)
FTshift_row = np.empty([nrows,ncols],dtype=complex)
FTplot_row = np.empty([nrows,ncols])
IFT_row = np.empty([nrows,ncols],dtype=complex)
IFTplot_row = np.empty([nrows,ncols])

column = np.empty([nrows,ncols])
FT_col = np.empty([nrows,ncols],dtype=complex)
FTshift_col = np.empty([nrows,ncols],dtype=complex)
FTplot_col = np.empty([nrows,ncols])
IFT_col = np.empty([nrows,ncols],dtype=complex)
IFTplot_col = np.empty([nrows,ncols])


matrix_rows_fspace = np.empty([0,ncols])
matrix_cols_fspace = np.empty([0,nrows])

matrix_rows = np.empty([0,ncols])
matrix_cols = np.empty([0,nrows])


for i in range(0,nrows):
    line[i] = imagem[i,:]

    FT_row[i] = np.fft.fft(line[i])
#    FT_row[i] = np.fft.fftshift(FT_row[i])
#    FTplot_row[i] = np.log10(1+np.abs(FT_row[i]))
    matrix_rows_fspace = np.vstack((matrix_rows_fspace,FT_row[i]))

#    IFT_row[i] = np.fft.ifft(FTshift_row[i])
#    IFTplot_row[i] = np.log10(1+np.abs(IFT_row[i]))
    
#    matrix_rows = np.vstack((matrix_rows,IFTplot_row[i]))

for i in range(0,ncols):
    column[i] = imagem[:,i] #imports the column from imagem as a line!
#
    FT_col[i] = np.fft.fft(column[i])
#    FT_col[i] = np.fft.fftshift(FT_col[i])
#    FTplot_col[i] = np.log10(1+np.abs((FT_col[i])))
    matrix_cols_fspace = np.vstack((matrix_cols_fspace,FT_col[i]))    
    
    
#    IFT_col[i] = np.fft.ifft(FTshift_col[i])
#    IFTplot_col[i] = np.log10(1+np.abs((IFT_col[i])))
    
#    matrix_cols = np.vstack((matrix_cols,IFTplot_col[i]))

matrix_cols_fspace = np.transpose(matrix_cols_fspace)
#matrix_cols = np.transpose(matrix_cols)

final_matrix_fspace = np.add(matrix_rows_fspace,matrix_cols_fspace)
#final_matrix_fspace = matrix_rows_fspace
#final_matrix_fspace = matrix_cols_fspace
final_matrix_fspace = np.fft.fftshift(final_matrix_fspace)
final_matrix_fspace_plot = np.log10(1+np.abs(final_matrix_fspace))

#final_matrix = np.add(matrix_rows,matrix_cols)

IFT_1D = np.fft.ifft2(final_matrix_fspace)
IFTplot_1D = np.log10(1+np.abs(IFT_1D))
#IFTplot_1D = IFTplot_1D/np.amax(IFTplot_1D)


def plotting(image1,image2,label1,label2,filename):
    plt.subplot(121), plt.imshow(image1,cmap='gray'), plt.axis('off'), plt.title(label1)
    plt.subplot(122), plt.imshow(image2,cmap='gray'), plt.axis('on'), 
    plt.tick_params(axis='both', which='both',bottom='off', left='off',labelbottom='off', labelleft='off'), plt.title(label2),
    plt.savefig(filename, dpi=500, bbox_inches='tight'),
    plt.show()

#Plotting figures:
plotting(FTplot,final_matrix_fspace_plot,'2D Transform F-Space','1D+1D Transform F-Space','2Dvs1D_fspace')        
plotting(np.log10(1+np.abs(np.fft.fftshift(final_matrix_fspace))),IFTplot_1D,'No shift','1D+1D Transform','2Dvs1D')    
plotting(IFTplot,imagem,'2D Transform','Original','originalVs2DFT')    
#plotting(matrix_rows,matrix_cols,'Transform Row','Transform Column','1DFT')
 















#matrix = np.array([[1,2,3],[4,5,6],[7,8,9]])
#
#print(matrix)
#print(matrix[0])
#print(matrix[:,0])
