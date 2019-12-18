'''
Created on Apr. 01, 2019

@file    CktDef.py
@author  Evandro de Souza
@date    2019.04.01  
@version 0.1
@company University of Alberta - Computing Science
'''

from enum import Enum

class CKTState(Enum):
    OPEN  = 0   
    CLOSE = 1

class CKTPhase(Enum):
    PHASE_1   = 1
    PHASE_2   = 2
    PHASE_3   = 3
    PHASE_12  = 4
    PHASE_13  = 5
    PHASE_23  = 6
    PHASE_123 = 7    
    PHASE_ALL = 0

class CKTTerm(Enum):
    BUS1   = 1
    BUS2   = 2

class CKTProperty(Enum):
    VA = 1
    VB = 2
    VC = 3
    IA = 4
    IB = 5
    IC = 6
    PA = 7
    PB = 8
    PC = 9
    
    
    