# -*- coding: utf-8 -*-
"""
Created on Fri Nov 24 12:27:55 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting
import scipy as sp

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True) 

"""
This program simulates the Ernst equation (Eq. 18-14 at Haacke). The equation is calculated for "n_points" points, each corresponding to one angle "theta". 

The class "ratioEquation" is used to calculate the value of $T_1$

"""


n_points = 90 # number of angles to be used
theta = np.linspace(1,n_points,n_points) #array with angle values

a_0  = 2 #index to select angle0
a_1  = 10 #index to select angle1

train = 43 
TR    = 3.78*10**-3       #Repetition time
#TR = TR*train
TE    = 1.813*10**-3      #Echo time
T2    = 72*10**-3         # T_2 Relaxation time 
            
SNR_list        = []        # list to append Signal-to-noise ratio values
T1_difference_list = []     # list to append difference between ideal and simulated T1 values with noise

class ratioEquation():
    
    def __init__(self,S1,S2,a1,a2,TR):
        self.S1 = S1
        self.S2 = S2
        self.a1 = a1 # angle1 in degrees
        self.a2 = a2 # angle2 in degrees
        self.TR = TR
    
    def defineEquation(self,T1):
        E1 = np.exp(-self.TR/T1)
        result = self.S1/self.S2 - np.sin(self.a1*np.pi/180)*(1-E1*np.cos(self.a2*np.pi/180)) / ( np.sin(self.a2*np.pi/180)*(1-E1*np.cos(self.a1*np.pi/180)) )    
        return result


for a in range(0,1):  
# Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)
    if a == 0: 
        T1 = 900*10**-3 # pre contrast 
    else:
        T1 = 200.3*10**-3 # pro contrast           
    

    for SNR in range(15,16): #vary SNR
        for i in range(1,2): #multiple runs with same T1


            E1 = np.exp(-TR/T1)
            thetaErnst = np.arccos(E1)*180/np.pi
#            print('Ernst_angle = {0:.2f}'.format(thetaErnst))
            

            rho0 = 1
            rho = rho0 * np.sin(theta*np.pi/180)*(1-E1) /(1-E1*np.cos(theta*np.pi/180))
            rho_without_noise = rho
            
            ratio = rho[a_1-1]/rho[a_0-1]
            print('Ratio = {0:.5f}'.format(ratio))
            
            SNR_list.append(SNR)
            StDev = rho[a_0]/SNR
            noise = np.random.normal(0,StDev,n_points)
#            rho = rho + noise 
                   
            S_0 = rho[a_0-1] #signal1 at angle index-1
            S_1 = rho[a_1-1] #signal2 at angle index-1
  
            equation = ratioEquation(S_0,S_1,a_0,a_1,TR) #initiate equation with constants

            T1_solved = sp.optimize.fsolve(equation.defineEquation,T1) #solve equation for T1
#            print(T1_solved)
            
#                if np.abs(fitted_T1) > 100:T1) > 100: 
#                #Fitting does not converge sometimes. It gives |T1| > 1000. We are desconsidering these points in this conditional.
#                    del SNR_list[-1] #removes last element of list
#                    continue         #skips current iteration

            difference = np.abs(T1_solved - T1)/T1
            difference = (T1_solved - T1)/T1
            T1_difference_list.append(difference*100)
##                        print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100)) 
##                            fit_x_points = np.linspace(X[0],X[1],1000)
##                            fitted_plot = model_equation(fitted_amplitude,TE,TR,fitted_T1,T2,fit_x_points)
##  

            '''PLOTTING'''
                         
            plt.figure(4)
            graph = plt.plot(theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
            plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
            plt.ylabel('Signal S')
#            plt.legend()
#            plt.savefig('signaltheta.png',dpi=600)
                    

            plt.figure(2)
            plt.plot(T1,ratio,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
            plt.xlabel(r'$T_1$',fontsize=16)
            plt.ylabel(r'$S_{10}/S_2$',fontsize=16)
#            plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(theta[a_0-1],theta[a_1-1],T1*1000),fontsize=16)
#            plt.savefig('uncertainty.png',dpi=600)

        
#            plt.figure(a)
#            plt.axvline(x=15, color='g', linestyle='-')
#            plt.plot(SNR_list,T1_difference_list,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
#            plt.xlabel('SNR',fontsize=16)
#            plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
#            plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(theta[a_0-1],theta[a_1-1],T1*1000),fontsize=16)
##            plt.savefig('uncertainty.png',dpi=600)




