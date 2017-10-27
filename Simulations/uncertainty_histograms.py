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
        self.index0      = 15 # 1 indicates angle of 2 degrees. Ideal is 15
        self.index1      = 80 # 9 indicates angle of 10 degrees. Ideal is 80

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
        self.difference_list = []
        
        delta = 100
#        for i in range(700,700+delta,delta):
        
        self.X0_array = np.empty(0)
        self.X1_array = np.empty(0)
        self.Y0_array = np.empty(0)
        self.Y1_array = np.empty(0)
        
        self.counter = 0

        for SNR in range(15,16): #vary SNR
            for i in range(0,233): #multiple runs with same T1
            
                for j in range(0,1):
                    if j == 0:  
                        T1 = 613.9*10**-3 # pre contrast 
                    else:
                        T1 = 200.3*10**-3 # pro contrast 

                    E1 = np.exp(-self.TR/T1)
                    
                    thetaErnst = np.arccos(E1)*180/np.pi
    #                print('Ernst_angle = {0:.2f}'.format(thetaErnst))
                    
#     Why did I use 3 as the amplitude below? I think I got this value from the data. 
                    ampIdeal = 3 / (np.sin(2*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(2*np.pi/180))) 
                    rho0 = ampIdeal
#                    rho0 = 1

                    rho = rho0 * np.sin(self.theta*np.pi/180)*(1-E1)*np.exp(-self.TE/self.T2)/(1-E1*np.cos(self.theta*np.pi/180))
                    rho_nonoise = rho

#   Find best angles according to Deoni 2003:
                    maximum = np.amax(rho)
                    rho_at_best_angles = 0.71*maximum
                    
                    SNR_list.append(SNR)
                    StDev = rho[self.index0]/SNR
                    print(StDev)
                    noise = np.random.normal(0,StDev,self.n_points)
                    rho = rho + noise 
                    
                    rho_sin = np.divide(rho,self.sin_theta)
                    rho_tan = np.divide(rho,self.tan_theta)
                    
        #    Linearization Y = alpha*X + beta for theta = 2 and 10 degrees
                    Y = np.empty(2)
                    X = np.empty(2)
                
                    Y[0] = rho[self.index0]/self.sin_theta[self.index0]
                    Y[1] = rho[self.index1]/self.sin_theta[self.index1]
                    X[0] = rho[self.index0]/self.tan_theta[self.index0]
                    X[1] = rho[self.index1]/self.tan_theta[self.index1]

    
                    coef_angular = (Y[0]-Y[1])/(X[0]-X[1])
    #                print('\nHand angular coef = {0:.6e}'.format(coef_angular))

#                    if coef_angular < 0:
                    if (Y[0]-Y[1]) < 0 or (X[0]-X[1]) < 0:

                        self.counter+=1
#                        print('\nA negative angular coefficient was calculated! This indicates noise that is too high!')
#                        print('This (SNR, i) pair will be neglected from the analysis and it will not be saved.')
                        del SNR_list[-1]
                        break
                    else:
                        
                        self.X0_array = np.append(self.X0_array,rho[self.index0])
                        self.X1_array = np.append(self.X1_array,rho[self.index1])
                        self.Y0_array = np.append(self.Y0_array,Y[0])
                        self.Y1_array = np.append(self.Y1_array,Y[1])
                        
                        T1_hand = - self.TR/np.log(coef_angular)

                        params = Parameters()
                        params.add('amplitude', value=100) #value is the initial value for fitting
                        params.add('T1', value = 0.05, min = 0, max=2)
                    
                        fitting = minimize(self.residual, params, args=(X, Y))
                            
                        if fitting.success == False: 
                            print('\nFitting was NOT successful:')
                        else:
                            self.fitted_amplitude = fitting.params['amplitude'].value
                            self.fitted_T1 = fitting.params['T1'].value
#                            print('    Fitted Amplitude = {0:.2e}'.format(self.fitted_amplitude))
#                            print('    Fitted T1        = {0:.2e}'.format(self.fitted_T1))
#                            print('    Hand T1          = {0:.2e}'.format(T1_hand))
            
        
#                            difference = np.abs(self.fitted_T1 - T1)/T1
                            difference = (self.fitted_T1 - T1)/T1
                            self.difference_list.append(difference*100)
    #                        print('    Difference between fitted and simulated T1 is {0:.5f}%'.format(difference*100))
         
    #                            self.fit_x_points = np.linspace(X[0],X[1],1000)
    #                            self.fitted_plot = self.model_equation(self.fitted_amplitude,self.TE,self.TR,self.fitted_T1,self.T2,self.fit_x_points)
    #                           
                            plt.figure(4)
    #                        graph = plt.axhline(y=rho_at_best_angles, color='y', linestyle='-',label ='71\% of A maximum')
    #                        graph = plt.axvline(x=thetaErnst, color='blue', linestyle='-')
                            graph = plt.plot(self.theta,rho, label='Signal A + noise 'r'$\sigma$',linewidth=2)
                            graph = plt.plot(self.theta,rho_nonoise,label='Signal A',linewidth=3)
    #                        graph = plt.plot(self.theta,rho2,label='Signal B',linewidth=2)
        #                        graph = plt.plot(theta,rhoapp,'ro')
                            plt.xlabel('Flip angle 'r'$\theta$ [Degrees]')
                            plt.ylabel('Signal S')
    #                        plt.legend()
    #                        plt.savefig('signaltheta.png',dpi=600)
                                
                            plt.figure(5)
        #                    graph1 = plt.plot(rho_tan,self.fitted_plot)
        #                    graph1 = plt.plot(X,Y,'o')                    
                            graph1 = plt.plot(X,Y,'o')#,label='Pontos p/ 'r'$\theta_1 = 2$ e $\theta_2 = 10$')
        #                    graph1 = plt.plot(self.fit_x_points,self.fitted_plot)#, label ='Reta de ajuste')
                            plt.xlabel('Sinal / tangente')
                            plt.ylabel('Sinal / seno')
        #                    plt.legend()
            #                plt.show()
    #                        plt.savefig('linear2.png')
            
                            plt.figure(j)
                            plt.axvline(x=15, color='g', linestyle='-')
                            plt.plot(SNR_list,self.difference_list,'o',c='#ED8F19',markeredgecolor='black',markeredgewidth=0.5)
                            plt.xlabel('SNR',fontsize=16)
    #                        plt.ylabel(r'$\Delta \% T_1$',fontsize=16)
    #                        plt.title(r'$\theta_1 = {0:.0f} \quad   \theta_2 = {1:.0f}  \quad  T_1 = {2:.0f}$ ms'.format(self.theta[self.index0],self.theta[self.index1],T1*1000),fontsize=16)
    
    
    #            plt.savefig('uncertainty.png',dpi=600)

        print('# de pontos ignorados = {0:.0f}'.format(self.counter))
        self.difference_list = np.asarray(self.difference_list)
        bins = 100
        croped_pixel_array = np.loadtxt('croped_pixel_array.txt')
        croped_pixel_array = np.ravel(croped_pixel_array) #transform 2D to 1D array

        print(np.sum(np.histogram(croped_pixel_array)[0]))
        print(np.sum(np.histogram(self.X0_array)[0]))
        print(np.sum(np.histogram(self.X1_array)[0]))
        print(np.sum(np.histogram(self.Y0_array)[0]))
        print(np.sum(np.histogram(self.Y1_array)[0]))


        plt.figure(10)
        plt.hist(croped_pixel_array-np.median(croped_pixel_array),bins=bins,label='Data',alpha=0.3)

        plt.hist((self.X0_array-np.median(self.X0_array))/np.amax(self.X0_array),bins=bins,label='X_2',alpha=0.3)
        plt.hist((self.X1_array-np.median(self.X1_array))/np.amax(self.X1_array),bins=bins,label='X_10',alpha=0.3)
      
#        plt.hist((self.Y0_array-np.median(self.Y0_array))/np.amax(self.Y0_array),bins=bins,label='Y_2',alpha=0.3)
#        plt.hist((self.Y1_array-np.median(self.Y1_array))/np.amax(self.Y1_array),bins=bins,label='Y_10',alpha=0.3)
        plt.legend()
#        x1,x2,y1,y2 = plt.axis()
#        plt.axis((x1,x2,0,5))
        
        plt.figure(11)
        plt.hist((self.difference_list)/np.amax(self.difference_list),bins=bins,label="Dif",alpha=0.5)
        plt.legend()
#        x1,x2,y1,y2 = plt.axis()
#        plt.axis((-0.9,0.9,0,40))

        
        print(np.shape(croped_pixel_array))
        print(np.shape(self.X0_array))
        print(np.shape(self.difference_list))
        
        
        

a = main()
a.calculations()















