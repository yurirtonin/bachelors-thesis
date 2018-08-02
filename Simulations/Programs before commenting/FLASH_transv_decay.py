#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys #System functions, such as reading from standard input (usually keyboard) 

from math import exp #Dump everything in module "math" into the local namespace;

from scipy.constants import hbar, pi, k # Get physical constants (e.g. planck h, hbar)

import matplotlib.pyplot as plt

import numpy as np

import pylab

#from prettytable import PrettyTable

N = 1000

T1 = 809*10**-3
T2 = 34*10**-3
TR = 10*T2
M0 = 1

E1 = np.exp(-TR/T1)
E2 = np.exp(-TR/T2)

#Angles in Degrees
start_angle = 4 
end_angle = 30

#print('E1 = {0:.2e}'.format(E1))
#print('E2 = {0:.2e}'.format(E2))

my_zero = M0*10**-4 #0.01% of initial value

t = np.linspace(0,TR,N)

#tabela = PrettyTable(['Angle','f(0)' ,'t of f(t)=0'])

for a in range(start_angle,end_angle+1,2):
            
    M_transv = M0 * np.sin(a*np.pi/180)*(1-E1)*np.exp(-t/T2)/(1-E1*np.cos(a*np.pi/180))
    
    plt.figure(0)
    if a == start_angle or a == end_angle:
        graph1 = plt.plot(t,M_transv, label = ' Ângulo = {0:d}°'.format(a))
    else: graph1 = plt.plot(t,M_transv)
    plt.legend(loc = 'best')
    
    for i in range(len(M_transv)):
        if M_transv[i] < my_zero: 
#            tabela.add_row([a,'{0:.2f}'.format(M_transv[0]),'{0:.2e}'.format(t[i])])
            break

print(tabela)                    

plt.ylabel('Magnetização transversal')
plt.xlabel('Tempo [segundos]')
plt.show()
   

#goal: fazer reverso pra determinar T1
#entender como arquivo de dado médico é organizado
#   jpeg, tif, 
# diferença im medica pra tradicional: criou padrao
#padrao dicom foi criado
#vantagem do fomrato: carrega informaçao dos parametros da imagem
#mipav baixar
#estudar o que é arquivo dicom
#tirar informações do header 
#dicominfo funcao matlab 
#descobrir como ordenar os dados (criar imagem a partir da coluna gigante de valores
#encontrar informações da geometria no arquivo dicom
#programa que abre o arquivo dicom em um determinado corte da imagem, com um determinado eco
#brincar com pasta 601
#uma vez que tenho as informações, ler o dado e mostrar imagem

#dicom conformance statement


#depois teremos que ter toda a estrutura de abrir arquivo, verificar e de fazer processamento

    
    
    
    
    
    
    
    
    
    
