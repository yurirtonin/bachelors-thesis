# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 10:46:59 2017

@author: Yuri Tonin
"""

import numpy as np
import matplotlib.pyplot as plt
from lmfit import minimize, Parameters # lmfit is the package for fitting


class main():
    
    def __init__(self):
        
        #rho0 = 8.14
        a = 90
        self.n_points = a
        self.theta = np.linspace(1,a,self.n_points)
#        print(self.theta)
        self.sin_theta = np.sin(self.theta*np.pi/180)
        self.tan_theta = np.tan(self.theta*np.pi/180)

        self.index_2deg  = 1
        self.index_10deg = 9
        self.index2      = 4
        self.index3      = 11
        self.index4      = 14

        train = 43
        self.TR = 3.78*10**-3*train
        self.TE = 1.813*10**-3 
        self.T2 = 72*10**-3
        #self.T1 = 678*10**-3
    
        print(self.TR/0.7)
    
    def residual(self,params, x, data):
        # Parameters to be fitted must be declared below
        amplitude = params['amplitude']
        T1 = params['T1']
        # T2 = params['T2']
    
        model = self.model_equation(amplitude,self.TE,self.TR,T1,self.T2,x)
    
        return (data - model)
    
    def model_equation(self,a,TE,TR,T1,T2,x): # x is the flip angle
        E1 = np.exp(-TR/T1)
        b = a*(1-E1)*np.exp(-TE/T2)
        return E1*x+b
    
    def calculations(self):
            
        SNR_list = []
        difference_list = []
        
        delta = 100
#        for i in range(700,700+delta,delta):
        
        for j in range(4,35): #vary SNR
            for i in range(1,30): #multiple runs with same T1
                i = 700
                T1 = i*10**-3
                
#                print('\n===== // ===== // ===== // ===== // ===== // =====')
#                print('\nT1 = {0:.2e}'.format(T1))
#                print('TR = {0:.2e}'.format(self.TR))
            
                E1 = np.exp(-self.TR/T1)
                
                thetaErnst = np.arccos(E1)*180/np.pi
#                print('Ernst_angle = {0:.2f}'.format(thetaErnst))
                
                ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
                rho0 = ampIdeal
                    
                rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180)) 
                #    rhoapp = rho0 * theta / (1+0.5*E1*theta**2/(1-E1))
    
    #            maximum = np.amax(rho)
    #            coef = 10**-2
    #            noise = coef*maximum*np.random.random_sample(self.n_points)
    #            print('\nNoise is {0:.5f}% of the maximum of the function'.format(coef*100))
    
#                print()
#                print(rho[self.index_2deg],rho[self.index_10deg])
#                print(self.sin_theta[self.index_2deg],self.sin_theta[self.index_10deg])
#                print(np.divide(rho,self.sin_theta)[self.index_2deg],np.divide(rho,self.sin_theta)[self.index_10deg])
#                print(np.divide(rho,self.tan_theta)[self.index_2deg],np.divide(rho,self.tan_theta)[self.index_10deg])
    
    #            print(rho_tan[self.index_2deg],rho_tan[self.index_10deg])
    #            print(np.divide(rho,self.sin_theta)[0:5])
    #            print(np.divide(rho,self.tan_theta)[0:5])
                
                SNR = j
                SNR_list.append(SNR)
                StDev = rho[self.index_2deg]/SNR
                noise = StDev*np.random.random_sample(self.n_points)*1
                rho = rho + noise 
#                print('\nNoise is at most the Standard Deviation = {0:.5f}'.format(StDev))
                
                rho_sin = np.divide(rho,self.sin_theta)
                rho_tan = np.divide(rho,self.tan_theta)
                
#                print()
#                print(rho[self.index_2deg],rho[self.index_10deg])
#                print(rho_sin[self.index_2deg],rho_sin[self.index_10deg])
#                print(rho_tan[self.index_2deg],rho_tan[self.index_10deg])
                
    #            print(np.subtract(rho_sin,rho_tan))
                
                
    #    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                Y = np.empty(2)
                X = np.empty(2)
            
                Y[0] = rho[self.index_2deg]/self.sin_theta[self.index_2deg]
                Y[1] = rho[self.index_10deg]/self.sin_theta[self.index_10deg]
                X[0] = rho[self.index_2deg]/self.tan_theta[self.index_2deg]
                X[1] = rho[self.index_10deg]/self.tan_theta[self.index_10deg]
                
#                Y[2] = rho[self.index2]/self.sin_theta[self.index2]
#                X[2] = rho[self.index2]/self.tan_theta[self.index2] 
#                Y[3] = rho[self.index3]/self.sin_theta[self.index3]
#                X[3] = rho[self.index3]/self.tan_theta[self.index3] 
#                Y[4] = rho[self.index4]/self.sin_theta[self.index4]
#                X[4] = rho[self.index4]/self.tan_theta[self.index4]  
               
  
                coef_angular = (Y[1]-Y[0])/(X[1]-X[0])
#                print('\nHand angular coef = {0:.6e}'.format(coef_angular))
                T1_hand = - self.TR/np.log(coef_angular)
                
                params = Parameters()
                params.add('amplitude', value=100) #value is the initial value for fitting
                params.add('T1', value = 0.05)
            
                fitting = minimize(self.residual, params, args=(X, Y))
                if fitting.success: 
#                    print('\nFitting was successful:')
                
                    self.fitted_amplitude = fitting.params['amplitude'].value
                    self.fitted_T1 = fitting.params['T1'].value
#                    print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                    print('    Fitted T1        = {0:.2e}'.format(self.fitted_T1))
#                    print('    Hand T1          = {0:.2e}'.format(T1_hand))
    
                    
                    difference = np.abs(self.fitted_T1 - T1)/T1
                    difference_list.append(difference*100)
#                    print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
                    
                    self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,rho_tan)
                   
                    plt.figure(0)
                    graph = plt.plot(self.theta,rho)#,'bo')
    #                graph = plt.plot(theta,rhoapp,'ro')
                    plt.xlabel('Flip angle')
                    plt.ylabel('Signal')
    
                    plt.figure(1)
#                    graph1 = plt.plot(rho_tan,self.fitted_plot)
                    graph1 = plt.plot(X,Y,'o')
                    plt.xlabel('Signal/tan')
                    plt.ylabel('Signal/sin')
    #                plt.show()
    
                    plt.figure(2)
                    graph2 = plt.plot(SNR_list,difference_list,'ro')
                    plt.xlabel('SNR')
                    plt.ylabel('(T1_fit - T1)*100/T1')
                    plt.title('Angle1 = {0:.2f}     Angle2 = {1:.2f}'.format(self.theta[self.index_2deg],self.theta[self.index_10deg]))


a = main()
a.calculations()

















