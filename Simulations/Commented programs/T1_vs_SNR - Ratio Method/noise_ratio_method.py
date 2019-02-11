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
 
'''
This program calculates the Ernst equation with and without noise. For each equation
with noise, we extract the value of T1 from the "ratio method". In the end, we plot
the percentual variation of T1 (in comparison to the ideal value) vs the SNR.
'''


n_points = 180
theta = np.linspace(1,n_points,n_points)

index0  = 2
index1  = 16

TR    = 3.78*10**-3
TE    = 1.813*10**-3 
T2    = 72*10**-3
            
SNR_list        = []
difference_list = []

class equation():
    
    def __init__(self,S1,S2,a1,a2,TR):
        self.S1 = S1
        self.S2 = S2
        self.a1 = a1
        self.a2 = a2
        self.TR = TR
    
    def defineEquation(self,T1):
        E1 = np.exp(-self.TR/T1)
        result = self.S1/self.S2 - np.sin(self.a1)*(1-E1*np.cos(self.a2)) / ( np.sin(self.a2)*(1-E1*np.cos(self.a1)) )    
        return result


for a in range(0,1):  
# Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)
    if a == 0: 
        T1 = 613.9*10**-3 # pre contrast 
    else:
        T1 = 200.3*10**-3 # pro contrast           
    

    for j in range(5,40): #vary SNR
        for i in range(1,30): #multiple runs with same T1
                 
            E1 = np.exp(-TR/T1)
            thetaErnst = np.arccos(E1)*180/np.pi            
            
            rho0 = 100
                       
            rho = rho0 * np.sin(theta*np.pi/180)*(1-E1) /(1-E1*np.cos(theta*np.pi/180))
            rho_without_noise = rho
                        
            SNR = j
            SNR_list.append(SNR)
            StDev = rho[index0]/SNR
            noise = np.random.normal(0,StDev,n_points)
            rho = rho + noise 
                   
            S1 = rho[index0-1]
            S2 = rho[index1-1]
            a1 = (index0*np.pi/180)  
            a2 = (index1*np.pi/180)           
  
            myEquation = equation(S1,S2,a1,a2,TR)
            T1_solved = sp.optimize.fsolve(myEquation.defineEquation,T1)
            
#            if np.abs(T1_solved) > 100: 
#            #Fitting does not converge sometimes. It gives |T1| > 100. We are desconsidering these points in this conditional.
#                del SNR_list[-1] #removes last element of list
#                continue         #skips current iteration

            difference = np.abs(T1_solved - T1)/T1
            difference_list.append(difference*100)#            

#            print('\n===== // ===== // ===== // ===== // ===== // =====')
#            print('\nT1 = {0:.2e}'.format(T1))
#            print('TR = {0:.2e}'.format(TR))            
#            print('Ernst_angle = {0:.2f}'.format(thetaErnst))
#            print(rho[index1-1]/rho[index0-1])
#            print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
#            print('===== // ===== // ===== // ===== // ===== // =====')
                      
            plt.figure(4)
            graph = plt.plot(theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
            plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
            plt.ylabel('Signal S')
#            plt.legend()
#            plt.savefig('signaltheta.png',dpi=600)
                    
        
            plt.figure(a)
            plt.axvline(x=15, color='g', linestyle='-')
            plt.plot(SNR_list,difference_list,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
            plt.xlabel('SNR',fontsize=16)
            plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
            plt.ylim(0, 150)
            plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(theta[index0-1],theta[index1-1],T1*1000),fontsize=16)
    plt.savefig('uncertainty.png',dpi=600)



