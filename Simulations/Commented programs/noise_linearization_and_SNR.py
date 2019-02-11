# -*- coding: utf-8 -*-
"""
Created on Thu Sep 21 12:10:29 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting

#from matplotlib import rc
#rc('font',**{'family':'sans-serif','serif':['Computer Modern Roman']})
#rc('text', usetex=True)

'''
This programm calculates the two points of the linearization method for many
runs with the same T1 value but with different noise. The Ernst equation is plotted
without any noise on top of all the equations+random_noise. A second plot shows the distribution
of the pair of points of the linearization method in the same plot. 
'''

class main():
    
    def __init__(self):
        
        self.n_points = 180 #number of angles
        self.theta = np.linspace(1,self.n_points,self.n_points) #array with angle values
        self.sin_theta = np.sin(self.theta*np.pi/180) #array with sine of angles
        self.tan_theta = np.tan(self.theta*np.pi/180) #array with tangent of angles

        self.index0 = 1 #index to select first angle from "theta" array
        self.index1 = 9 #index to select second angle

        self.TR = 3.789*10**-3
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        self.T1 = 613.9*10**-3  # Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)    
    
    def residual(self,params, x, data):
    # Parameters to be fitted must be declared below
        amplitude = params['amplitude']
        T1 = params['T1']
        # T2 = params['T2']
        model = self.model_equation(amplitude,self.TE,self.TR,T1,self.T2,x)
        return (data - model)
        
    def model_equation(self,a,TE,TR,T1,T2,x): # x is the flip angle
        E1 = np.exp(-TR/T1)
        b = a*(1-E1)#*np.exp(-TE/T2)
        return E1*x+b
    
    def calculations(self):
            
        SNR_list = []
        self.difference_list = []
                
        self.X0_array = np.empty(0) #declaring empty arrays to save (x,y) values of each point
        self.X1_array = np.empty(0) 
        self.Y0_array = np.empty(0)
        self.Y1_array = np.empty(0)

        for j in range(5,30): #vary SNR
            for i in range(1,30): #multiple runs with same T1
                print('SNR = {0:.0f}; Run #{1:0.0f}'.format(j,i))
            
                E1 = np.exp(-self.TR/self.T1)
                thetaErnst = np.arccos(E1)*180/np.pi
                
#                print('\n===== // ===== // ===== // ===== // ===== // =====')
#                print('\nT1 = {0:.2e}'.format(self.T1))
#                print('TR = {0:.2e}'.format(self.TR))                
#                print('Ernst_angle = {0:.2f}'.format(thetaErnst))
                
                rho0 = 100     
                rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                rho_without_noise = rho
    
# rho2 is a second 'ideal' Ernst curve, in case you want to compare two different ones                
                T12 = 1000*10**-3
                E12 = np.exp(-self.TR/T12)
                rho2 = rho0 * np.sin(self.theta*np.pi/180)*(1-E12)*np.exp(-self.TE/self.T2)/(1-E12*np.cos(self.theta*np.pi/180))
# === # === # === # === # === # === # === # === # === # === # === # === # === #
               
#   Find best angles according to Deoni 2003:
                maximum = np.amax(rho)
                rho_at_best_angles = 0.71*maximum
                find_rho = rho
                best_angle = (np.abs(find_rho-rho_at_best_angles)).argmin() #returns the minimum values along the axis
                find_rho = np.delete(find_rho,best_angle) #delete first best angle, so the function can find the next with the subsequent .argmin() command
#                for i in range(1,2): 
#                    find_rho = np.delete(find_rho,best_angle+i)
#                    find_rho = np.delete(find_rho,best_angle-i)
                best_angle2 = (np.abs(find_rho-rho_at_best_angles)).argmin()
#                print('Ideal angles are: {0:.0f} and {1:.0f}\n'.format(best_angle2,best_angle))
# === # === # === # === # === # === # === # === # === # === # === # === # === #

                SNR = j
                SNR_list.append(SNR)
                StDev = rho[self.index0]/SNR #defining standard deviation 
                noise = np.random.normal(0,StDev,self.n_points) #noise is a gaussian distribution
                rho = rho + np.abs(noise) #signal with noise
#                print('\nNoise is at most the Standard Deviation = {0:.5f}'.format(StDev))
                
                rho_sin = np.divide(rho,self.sin_theta) #signal/sine for linearization method
                rho_tan = np.divide(rho,self.tan_theta) #signal/tan  for linearization method
                
#    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                Y = np.empty(2)
                X = np.empty(2)            
                Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                X[0] = rho[self.index0]/self.tan_theta[self.index0]
                X[1] = rho[self.index1]/self.tan_theta[self.index1] 

                self.X0_array = np.append(self.X0_array,X[0])
                self.X1_array = np.append(self.X1_array,X[1])
                self.Y0_array = np.append(self.Y0_array,Y[0])
                self.Y1_array = np.append(self.Y1_array,Y[1])
  
                coef_angular = (Y[0]-Y[1])/(X[0]-X[1]) #manual calculation of angular coefficient of the line that connects pair of points (X0,Y0) and (X1,Y1)
#                print('\nHand angular coef = {0:.6e}'.format(coef_angular))
                if coef_angular < 0:
                    print('\nA negative angular coefficient was calculated! This indicates noise that is too high!')
                T1_hand = - self.TR/np.log(coef_angular)
                
# Linear fit                
                params = Parameters()
                params.add('amplitude', value=100) #value is the initial value for fitting
                params.add('T1', value = 0.05, min = 0, max=2)
            
                fitting = minimize(self.residual, params, args=(X, Y))
                
                if fitting.success == False:
                    print('\nFitting was NOT successful')
                else:
#                    print('\nFitting was successful:')
                
                    self.fitted_amplitude = fitting.params['amplitude'].value
                    self.fitted_T1 = fitting.params['T1'].value
#                    print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                    print('    Fitted T1        = {0:.2e}'.format(self.fitted_T1))
#                    print('    Hand T1          = {0:.2e}'.format(T1_hand))
    
                    if np.abs(self.fitted_T1) > 100: 
#                   Fitting does not converge sometimes. It gives |T1| > 1000. We are desconsidering these points in this conditional.
                        print('Fitting result in a value too high for T1 (>100). This point will be disconsidered')
                        del SNR_list[-1] #removes last element of list
                        continue         #skips current iteration

                    difference = np.abs(self.fitted_T1 - self.T1)/self.T1 #percentual difference between T1 from ideal and from noisy signal
                    self.difference_list.append(difference*100)
#                    print('Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
 
# Following to declarations are used to plot the fitting line between points ahead
                    self.fit_x_points = np.linspace(X[0],X[1],1000)
                    self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)

#PLOT OF ERNST EQUATION WITHOUT NOISE ON TOP OF ERNST EQUAITONS WITH NOISE
                    a = plt.figure(4)
#                    graph = plt.axhline(y=rho_at_best_angles, color='y', linestyle='-',label ='71\% of A maximum')
#                    graph = plt.axvline(x=thetaErnst, color='blue', linestyle='-')
                    graph = plt.plot(self.theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
                    graph = plt.plot(self.theta,rho_without_noise,label='Signal A',linewidth=3,color='yellow')
#                    graph = plt.plot(self.theta,rho2,label='Signal B',linewidth=2)
                    plt.xlabel('Ângulo de Flip 'r'$\theta$ [Degrees]')
                    plt.ylabel('Sinal')
#                    plt.legend()
                    if j == 29 & i==29: plt.savefig('signaltheta.png',dpi=600)
                 
#LINEARIZATION POINTS FOR ALL THE ERNST EQUATIONS THAT WERE CALCULATED                    
                    plt.figure(5)
#                    graph1 = plt.plot(rho_tan,self.fitted_plot)
#                    graph1 = plt.plot(X,Y,'o')    
                    graph1 = plt.plot(X,Y,'o')#,label='Pontos p/ 'r'$\theta_1 = 2$ e $\theta_2 = 10$')
#                    graph1 = plt.plot(self.fit_x_points,self.fitted_plot)#, label ='Reta de ajuste')
                    plt.xlabel('Sinal / tangente')
                    plt.ylabel('Sinal / seno')
#                    plt.legend()
                    if j == 29 & i==29: plt.savefig('linear2.png',dpi=600)

# PERCENTUAL VARIATION OF T1 (COMPARING TO IDEAL) vs SNR
                    plt.figure(1)
                    plt.axvline(x=15, color='g', linestyle='-')
#                    plt.axhline(y=50, color='black', linestyle=':')
#                    plt.axhline(y=100, color='red', linestyle=':')
                    plt.plot(SNR_list,self.difference_list,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
                    plt.xlabel('SNR',fontsize=16)
                    plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
#                    plt.ylim(0,120)
                    plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_R = {2:.3f}$ ms'.format(self.theta[self.index0],self.theta[self.index1],self.TR*1000),fontsize=16)
                    if j == 29 & i==29: plt.savefig('uncertainty.png',dpi=600)
                     
        
a = main()
a.calculations()
















