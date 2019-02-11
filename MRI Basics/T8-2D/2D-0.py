#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 27 21:07:03 2017

@author: YuriRT
"""

import sys
import numpy as np
import cmath
from math import *
from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)
import matplotlib.pyplot as plt
import pylab
import peakutils
from PIL import Image
import matplotlib.image as mplim
import time

start_time = time.time()


Temp     = 300             # Temperature [Kelvin]
rho      = 110.4*6*10**23  # Number of protons per liter in water
gammaRad   = 2.68*10**8      # Proton gyromagnetic ratio [rad/s/Tesla]
gammaHz = 42.6*10**6      # Proton gyromagnetic ratio [Hz/Tesla]
gamma2pi = (gammaHz/(2*pi))#*10**-4 #Herz/Gauss
B0       = 1               # Static magnetic field in z-direction [Tesla]
#Gx       = 3               # Gradient B-field [Gauss/centimeter] = 0.01*[Tesla/meter]
T2       = (100*10**-3)    # Decay time [seconds]
Tau      = 1#1000000*10**-3
gamma2pi = 1.0

#Initial magnetization
M = rho*(gammaRad**2)*(hbar**2)*B0/(4*k*Temp)
M=1

n = 50 # Number of points. MUST BE EVEN.
print('\n Number of points: n = {0:.0f} \n'.format(n))

# Opening original image to be transformed
img = Image.open('image50.png').convert('L') #Converting to grayscale
img.save('greyscale.png') #Saving grayscale image
imagem = mplim.imread('greyscale.png')

density_matrix = np.zeros([n,n],dtype=float)
k_space = np.zeros([n,n],dtype=complex)

a=2
for i in range(np.int((n-1)/2)-2*a,np.int((n-1)/2)+2*a):
    for m in range(np.int((n-1)/2)-a,np.int((n-1)/2)+a):
        density_matrix[i][m] = 1.0
        
density_matrix = imagem

#density_matrix[2][10] = 1
#density_matrix[10][2] = 0.5
        
x_position_array = np.empty([n],dtype=float)
y_position_array = np.empty([n],dtype=float)

DX = 0.1 #cm
DY = DX

for i in range(0,n):
    x_position_array[i] = i*DX
    y_position_array[i] = i*DY

# Creating time array
total_time = 1 # Signal acquisition time in [seconds]
dt = total_time/n
time_array = np.empty([n],dtype=float)
for i in range(0,n):
    time_array[i] = (-n/2)*dt+i*dt


# GENERATE SIGNAL #

def Exp(k,r):
    imaginary_exponential = cmath.exp(-1j*2*pi*k*r)
    return imaginary_exponential

def wExp(f,t):
    imaginary_exponential = np.exp(-1j*2*pi*f*t)
    return imaginary_exponential

def FID(magnetization,t,T,x_exponential,y_exponential):
#    SIL = magnetization * np.exp(-t/T) * x_exponential * y_exponential
    Signal = magnetization * x_exponential * y_exponential
    return Signal

G_phase = -0.1 # Initial phase gradient
deltaGy = 2*np.abs(G_phase)/n #deltaGy will be exact to make Gphase simetric around 0



G_read = 3

delta_kx = gamma2pi*G_read*dt
delta_ky = gamma2pi*deltaGy*Tau

print('delta Kx = {0:.2e}'.format(delta_kx))
print('delta Ky = {0:.2e}'.format(delta_ky))
print('1/n      = {0:.2e}'.format(1/n))


kspace_y = np.zeros(n)
kspace_x = np.zeros(n)

kspace_x = gamma2pi*G_read*time_array

for ky_line in range(0,n):
    
    start_loop_time = time.time()
    
#    if ky % 10 == 0: print('ky = {0:2d}'.format(ky))
    
    G_phase = G_phase + deltaGy
    
    for kx_line in range(0,np.int(n)): 

        signal = 0.0
        
        for y in range(0,n):
    
            #        print('    \n y = {0:2d}'.format(y))
            for x in range(0,n):
                
                magnetization = M*density_matrix[y][x]
                
                kx = gamma2pi*G_read*time_array[kx_line]
                ky = gamma2pi*G_phase*Tau

#                print(gamma2pi*G_read*x_position_array[x])

#                print(kx)
#                print(ky)
#                print('Mag = {0:.2f} '.format(magnetization))
#                print('   Exp X = {0:.2f}'.format(Exp(kx,x_position_array[x])))
#                print('      Exp Y = {0:.2f}'.format(Exp(ky,y_position_array[y])))
#                print('             FID = {0:.2f}'.format(FID(magnetization,0,T2,Exp(kx,x_position_array[x]),Exp(ky,y_position_array[y]))))

                

                signal = signal + FID(magnetization,0,T2,Exp(kx,x_position_array[x]),Exp(ky,y_position_array[y]))
            



        k_space[ky_line][kx_line] = signal
        kspace_y[ky_line] = ky


#        if ky_line % 20 == 0 and kx_line % 20 == 0: # if remainder of k/10 = 0
#            print('')
#            fig = plt.figure(figsize=(10,10))
#            plt.subplot(2,2,1)
#            plt.plot(k_space[:][kx_line]), plt.title('Line kx = {0:.2e}'.format(kx))
#            plt.subplot(2,2,2)
#            plt.plot(k_space[ky_line][:]), plt.title('Line ky = {0:.2e}'.format(ky))
#            plt.show()


    end_loop_time = time.time()
    print('Time spent in loop ky = {1:.2f} was {0:.2f} '.format(end_loop_time - start_loop_time,ky_line))

#k_space = np.fft.fftshift(k_space)
k_space = np.log10(1+np.abs(k_space))



IFT = np.fft.ifft2(k_space)
IFT = np.fft.fftshift(IFT)
IFTplot = np.log10(1+np.abs(IFT))
IFTplot = IFTplot/np.amax(IFTplot)

FT = np.fft.fft2(density_matrix)
FT = np.fft.fftshift(FT)
FT_plot = np.log10(1+np.abs(FT))
FT_plot = FT_plot/np.amax(FT_plot)

fig = plt.figure(figsize=(10,10))
plt.subplot(1,2,1)   
kspace_plot = plt.imshow(k_space,cmap='gray', origin='upper'), plt.axis('on'), #, plt.title('K-Space')
plt.savefig('k_space.png',dpi=500,bbox_inches='tight')
plt.subplot(1,2,2)
density_plot = plt.imshow(density_matrix,cmap='gray', origin='upper'), plt.axis('on')#, plt.title('X-Space')
plt.savefig('density.png',dpi=500,bbox_inches='tight')

fig2 = plt.figure(figsize=(10,10))
plt.subplot(2,2,1)
plt.imshow(IFTplot,cmap='gray'), plt.axis('off'), plt.title('IFT')
plt.savefig('IFT.png',dpi=500,bbox_inches='tight')
plt.subplot(2,2,2)
plt.imshow(FT_plot,cmap='gray'), plt.axis('off'), plt.title('FT')
plt.savefig('all_plots.png',dpi=500,bbox_inches='tight')


end_time = time.time()

print('Total time elapsed: {0:.2f} '.format((end_time - start_time)/60))


