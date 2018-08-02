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

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True)

'''
In this program we fix the time we want the acquisition to have, an then calculate how many
images can be acquired for each flip angle we may use. 
'''

M0 = 100 # initial magnetzation
   
T1 = 613.9*10**-3 # longitudinal relaxation time

TR= 162*10**-3

E1 = np.exp(-TR/T1)

number_of_angles = 90 #number of flip angles to be analyzed
    
total_time = 25 #seconds

images_array = np.empty(number_of_angles)
theta_array = np.empty(number_of_angles)

N = 200 #number of RF pulses that we use to analyze if steady state is reached
Mz_array = np.empty(N)
n_array  = np.empty(N)

distance_between_elements = 100 # constant to evaluate ahead in the code if steady state was reached 

for a in range(0,number_of_angles):
    
    theta = 1 + a #converter loop variable to double?
    
    theta_array[a] = theta # theta is flip angle in degrees

    Mz = M0 #initial Mz condition 

    for n in range(0,N):
        
        Mz = Mz*np.cos(theta*np.pi/180)*E1+ M0*(1-E1)
    
        Mz_array[n] = Mz
        n_array[n]  = n
    
    
    for n in range(0,N-distance_between_elements):
        
        difference = np.abs(Mz_array[n]-Mz_array[n+distance_between_elements])/Mz_array[n] #percentual difference between two Mz values
        if difference < 10**-5: #if difference between signal Mz is small enough, we consider that steady state was reached
            n_stable = n
            Mz_stable = Mz_array[n]
            break
          
    images_number = ((total_time - TR*n_stable) / TR)
    images_array[a] = images_number
    

    print('=== # === # === RESULTS === # === # === # ')
    print('Número de imagens que podem ser adquiridas em até 25 segundos: {0:.0f}'.format(images_number))
    print('Estabilidade atingida após {0:d} pulsos.'.format(n+1))
    print('Tempo total para aquisição: Ttotal = {0:.2f} segundos'.format(total_time))    
    print('=== # === # === # === # === # === # === # === # === # ')


plt.figure(1)
plt.plot(theta_array,images_array,'ro',markeredgecolor='black',markeredgewidth=0.5)
plt.xlabel('Angle [Degrees]',fontsize=16)
plt.ylabel('Number of images',fontsize=16)
plt.xticks(np.arange(min(theta_array)-1, max(theta_array)+5, 5.0))
#    plt.yticks(np.arange(100, 155, 10.0))
plt.title('Apnea time = {0:.0f} seconds'.format(total_time))
plt.grid(b=True,which='major',axis='both')    
plt.axes().set_aspect(1)
plt.savefig('images.png',dpi=600)


