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

class main():
    
    def __init__(self):
        
        self.n_points = 180
        self.theta = np.linspace(1,self.n_points,self.n_points)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        self.index0      = 1 # 1 indicates angle of 2 degrees. Ideal is 15
        self.index1      = 9 # 9 indicates angle of 10 degrees. Ideal is 80
#        self.index0      = 15 # 1 indicates angle of 2 degrees. Ideal is 15
#        self.index1      = 80 # 9 indicates angle of 10 degrees. Ideal is 80

        train = 43
        self.TR = 3.78*10**-3*train
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        #self.T1 = 678*10**-3
    
    
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
#        difference_list_A = []
        global_list = []
        
            
#                Besa values: T1 = 613.9 ms (pre) and T1 = 200.3 ms (post)

        for SNR in range(8,100): #vary SNR
#            print('\nSNR = {0:.0f}'.format(SNR))
            for i in range(1,20): #multiple runs with same T1
                
#                print("\nT1 run #{0:.0f}".format(i))                
#                print('\n===== // ===== // ===== // ===== // ===== // =====')
#                print('\nT1 = {0:.2e}'.format(T1))
#                print('TR = {0:.2e}'.format(self.TR))
            
                list_3pts = []

                for j in range(0,2):

                    if j == 0:  
                        T1 = 613.9*10**-3 # pre contrast 
                    else:
                        T1 = 200.3*10**-3 # pro contrast 

                    E1 = np.exp(-self.TR/T1)
#                    
#                        thetaErnst = np.arccos(E1)*180/np.pi
#                        print('Ernst_angle = {0:.2f}'.format(thetaErnst))
#                    
#     Why did I use 3 as the amplitude below? I think I got this value from the data. 
#                        ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
#                        rho0 = ampIdeal
    
                    rho0 = 1
                                   
                    rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                    rho_nonoise = rho 
                        
                    SNR_list.append(SNR)
                    StDev = rho[self.index0]/SNR
                    noise = np.random.normal(0,StDev,self.n_points)
                    rho = rho + noise 
#                    print('\nNoise is at most the Standard Deviation = {0:.5f}'.format(StDev))
                    
                    rho_sin = np.divide(rho,self.sin_theta)
                    rho_tan = np.divide(rho,self.tan_theta)
                    
#            Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                    Y = np.empty(2)
                    X = np.empty(2)
                
                    Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                    Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                    X[0] = rho[self.index0]/self.tan_theta[self.index0]
                    X[1] = rho[self.index1]/self.tan_theta[self.index1]
    
                    coef_angular = (Y[0]-Y[1])/(X[0]-X[1]) # Manually calculating angular coefficient to compare with value from fitting
                    
                    
                    if coef_angular < 0:
                        print('\nA negative angular coefficient was calculated! This indicates noise that is too high!')
                        print('This (SNR, i) pair will be neglected from the analysis and it will not be saved.')
                        list_3pts = []
                        break
#                        if j==0: 
#                            break # Skips for loop for the current (SNR, i) pair
#                        else: 
#                            j=1      # NEEDS TO DELETE THE DATA FROM THE PREVIOUS j=0 run.
                    
                    else:    
                        T1_hand = - self.TR/np.log(coef_angular) #Calculates T_1 with manually calculated angular coefficient
#                        print('Hand angular coef = {0:.6e}'.format(coef_angular))
                    
                        params = Parameters()
                        params.add('amplitude', value=100) #value is the initial value for fitting
                        params.add('T1', value = 0.05, min = 0, max=2)
                    
                        fitting = minimize(self.residual, params, args=(X, Y))
                        if fitting.success: 
#                            print('\nFitting was successful:')
                        
                            self.fitted_amplitude = fitting.params['amplitude'].value
                            self.fitted_T1 = fitting.params['T1'].value
                            
#                            print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                            print('    Fitted T11        = {0:.2e}'.format(self.fitted_T1))
#                            print('    Hand T1          = {0:.2e}'.format(T1_hand))
    
                            if j==0:
                                list_3pts.append(SNR)
                                list_3pts.append(self.fitted_T1)
                            else:
#                                if self.fitted_T1 > 10: print(self.fitted_T1)
                                list_3pts.append(self.fitted_T1)

#                    print(list_3pts)
    
                global_list.append(list_3pts) # When exits for loop for both T1's, recored vector (SNR,FittedT1A,FittedT1B) to another list
                global_list = [x for x in global_list if x != []] # Clear empty lists inside global list that were inserted for the case where angular coefficient < 0

#                print(global_list)                
    
        plt.figure(1)
        for i in range(len(global_list)):
            difference = np.abs(global_list[i][1] - global_list[i][2])*100/global_list[i][1]
#
            if difference > 150: print(global_list[i][1],global_list[i][2])
#        
#            print(difference)
#            print(global_list[i][0])
            plt.plot(global_list[i][0],difference,'ro')
            
            
#                        difference = np.abs(self.fitted_T1 - T1)/T1
#                        difference_list.append(difference*100)
#                        print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
     
#                            self.fit_x_points = np.linspace(X[0],X[1],1000)
#                            self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)
#                           

#                        plt.figure(j)
#                        plt.axvline(x=15, color='g', linestyle='-')
#                        plt.plot(SNR_list,difference_list,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
#                        plt.xlabel('SNR',fontsize=16)
#                        plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
#                        plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(self.theta[self.index0],self.theta[self.index1],T1*1000),fontsize=16)

#                        print('running')

#            plt.savefig('uncertainty.png',dpi=600)


a = main()
a.calculations()

















