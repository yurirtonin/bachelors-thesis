# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
# from mayavi import mlab

M0 = 100 # initial magnetzation
   
T1 = 700*10**-3 # longitudinal relaxation time

b = 1
TR_array = np.empty(b)
image_matrix = []
for i in range(0,b):
    
    dT = 2*10**-3
    TR = (162*10**-3 -(b/2)*dT) + i*dT # repetition time in seconds
    TR= 162*10**-3
    # print(TR)
    # TR = 162*10**-3
    TR_array[i] = TR
    
    E1 = np.exp(-TR/T1)
    
    thetaErnst = int(np.floor(np.arccos(E1)*180/np.pi))
    print('theta_Ernst = {0:d}'.format(thetaErnst))
    thetaErnst = 90
        
#    if i == 0: image_matrix = np.empty((0,thetaErnst))
    
    total_time = 25 #seconds
    
    images_array = np.empty(thetaErnst)
    theta_array = np.empty(thetaErnst)
    
    
    for a in range(0,thetaErnst):
        
        theta = 1 + a
        
        theta_array[a] = theta
    #    theta is flip angle in degrees
    
    #    print('Angle = {0:d}'.format(theta))
    
        N = 200
        Mz_array = np.empty(N)
        n_array  = np.empty(N)
        Mz = M0
        for n in range(0,N):
            
            Mz = Mz*np.cos(theta*np.pi/180)*E1+ M0*(1-E1)
        
            Mz_array[n] = Mz
            n_array[n]  = n
        
        plt.figure(0)    
        plt.plot(n_array,Mz_array)
        
        distance_between_elements = 100
        
        for n in range(0,N-distance_between_elements):
            
            difference = np.abs(Mz_array[n]-Mz_array[n+distance_between_elements])/Mz_array[n]
    #        print(difference)
            
            if difference < 0.0001:
                n_stable = n
                Mz_stable = Mz_array[n]
                break
            
        print('Estabilidade atingida após {0:d} pulsos.'.format(n+1))
        
        images_number = (total_time - TR*n_stable) / TR
        images_array[a] = images_number
        
    #    print('Número de imagens que podem ser adquiridas em até 25 segundos: {0:.0f}'.format(images_number))
    
      
    #    print('Tempo total para aquisição: Ttotal = {0:.2f} segundos'.format(total_time))
        
    #    if total_time >= Texame: print('Ângulo = {0:.0f} graus requer Texame > {1:f}'.format(theta,Texame))
        
    #    print('=== # === # === # === # === # === # === # === # === # ')
    
    
    plt.figure(1)
    plt.plot(theta_array,images_array,'o')
    
    image_matrix.append(images_array)

image_matrix = np.asarray(image_matrix)

print(image_matrix.shape)
print(theta_array.shape)
print(TR_array.shape)

fig = plt.figure()
ax = fig.gca(projection='3d')
theta_array, TR_array = np.meshgrid(theta_array, TR_array)
surf = ax.plot_surface(TR_array, theta_array, image_matrix, cmap=cm.coolwarm,linewidth=0, antialiased=False)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()

# s = mlab.surf(image_matrix,warp_scale='auto')
# s = mlab.surf(theta_array,TR_array,image_matrix)
# mlab.show()