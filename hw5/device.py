# written by Hao Yu
# 03.08.2016
import re
import sys
import os
import numpy as np
import scipy as sp
from scipy import sparse
from scipy.linalg import solve
import math
from hw5 import *

class NetlistParseError(Exception):
    """Netlist parsing exception."""
    pass
class Element:
    def __init__(self, word_set, counter):
        self.name = word_set[0]
        self.counter = counter
        del word_set[0]
        self.word_set = word_set

    def setAppend(self, word_set):
        self.word_set = self.word_set + word_set
    
    def isElement(self):
        return True
    def DealWithElement(self, fo):
        double_print(
            'Line#%d. The element is %s %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                   self.type, self.name,
                                                                                                   self.node1,
                                                                                                   self.node2,
                                                                                                   self.parameters), fo)

    def getDevice(self, isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):

        line=" ".join(self.word_set)
        #print line
        device = re.match(pat, line)
        Error = 0
        if device == None:
            if ~b1stline:
                double_print("Syntax error @ line %d" % self.counter, fo)
                Error = 1
                raise NetlistParseError()
        else:
            self.node1 = int(self.word_set[0])
            self.node2 = int(self.word_set[1])
        #print 'Error',Error
        if Error==0:
            if self.node1==0:
                ii=-1
            elif  self.node1 not in Node_list:
                ii=len(Node_list)
                Node_list.append(self.node1)
                node_counter+=1
            else:
                ii=Node_list.index(self.node1)

            if self.node2==0:
                jj=-1
            elif  self.node2 not in Node_list:
                jj=len(Node_list)
                Node_list.append(self.node2)
                node_counter+=1
            else:
                jj=Node_list.index(self.node2)
        else:
            raise NetlistParseError('Line%d'%self.counter)
        if isV:
            V_list.append((self.name,[ii,jj]))

        return  node_counter,V_list,Node_list

def martixGrow(G):
    tmp = np.zeros([1, G.shape[1]])
    G = np.row_stack((G, tmp))
    tmp = np.zeros([G.shape[0], 1])
    G = np.column_stack((G, tmp))
    return G
class Resistor(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list)=Element.getDevice(self,isV, pat,b1stline,fo,
            node_counter,V_list,exI_counter,I_list,Node_list)
        
        #self.value=eval(re.sub("(k)","e3",word_set[2]))
        self.value=eval(self.word_set[2])
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithR(self, fo):
        double_print(
            'Line#%d. The element is resistor %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                           self.name,
                                                                                                           self.node1,
                                                                                                           self.node2,
                                                                                                           self.word_set),
            fo)

    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        ii=-1
        jj=-1
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if ii!=-1 and jj!=-1:
            G[ii, jj] = G[ii, jj] - 1.0 / self.value
            G[jj, ii] = G[jj, ii] - 1.0 / self.value
            G[ii, ii] = G[ii, ii] + 1.0 / self.value
            G[jj, jj] = G[jj, jj] + 1.0 / self.value
        elif ii==-1 and jj!=-1:
            G[jj, jj] = G[jj, jj] + 1.0 / self.value
        elif jj==-1 and ii!=-1:
            G[ii, ii] = G[ii, ii] + 1.0 / self.value

        return (G,I,B,C,U,D)


class Vsrc(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+(dc\s+)?[0-9]+(k|m)?"
        isV=1
        (node_counter,V_list,Node_list)= Element.getDevice(self, isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        line=" ".join(self.word_set)
        #dc_value=re.match(pat,line)
        #dc_value=re.match("[0-9]+(k|m)?",line)
        #self.value=eval(re.sub("(k)","e3",dc_value))
        #ac_value=re.match("(ac)+\s+[0-9]+(k|m)?",line)
        #self.acMag=eval(re.sub("(k)","e3",ac_value))
        self.value=eval(self.word_set[2])
        #self.acMag=eval(self.word_set[4])

        I_list.append((self.name,exI_counter))
        exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithVsrc(self, fo):
        double_print('Line#%d. The element is voltage source %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (
        self.counter,
        self.name, self.node1, self.node2, self.parameters), fo)
    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
    	#print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            pp=I_list.get(self.name)
        else:
            raise NetlistParseError()
        if ii!=-1:
            C[pp,ii]+=1
            B[ii,pp]+=1
        if jj!=-1:
            C[pp,jj]-=1
            B[jj,pp]-=1
        I[pp,0]+=self.value

        return (G,I,B,C,U,D)
    def deStamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
    	#print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            pp=I_list.get(self.name)
        else:
            raise NetlistParseError()
       
        I[pp,0]-=self.value

        return (G,I,B,C,U,D)
    def DCStamp(self,G,I,B,C,U,D,V_list,I_list,Node_list,value):
    	#print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            pp=I_list.get(self.name)
        else:
            raise NetlistParseError()
        if ii!=-1:
            C[pp,ii]+=1
            B[ii,pp]+=1
        if jj!=-1:
            C[pp,jj]-=1
            B[jj,pp]-=1
        I[pp,0]+=value

        return (G,I,B,C,U,D)



class Isrc(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+(e-)?[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[2])


        return node_counter,V_list,Node_list,I_list,exI_counter


    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if ii!=-1:
            U[ii,0]-=self.value
        if jj!=-1:
            U[jj,0]+=self.value
        

        return (G,I,B,C,U,D)
    def DealWithIsrc(self, fo):
        double_print('Line#%d. The element is current source %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (
        self.counter,
        self.name, self.node1, self.node2, self.parameters), fo)


class VCVS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if Node_list.has_key(self.node3):
            mm=Node_list.get(self.node3)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node4):
            nn=Node_list.get(self.node4)
        else:
            raise NetlistParseError()

        if I_list.has_key(self.name):
            pp=Node_list.get(self.name)
        else:
            raise NetlistParseError()
            
        if pp!=-1:
            if ii!=-1:
                B[ii,pp]+=1
                C[pp,ii]+=1
            if jj!=-1:
                B[jj,pp]-=1
                C[pp,jj]-=1
            if mm!=-1:
                V[pp,mm]-=self.value
            if nn!=-1:
                V[pp,nn]+=self.value

        return (G,I,B,C,U,D)
    def getDevice(self,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[4])
        self.node3=eval(self.word_set[2])
        self.node4=eval(self.word_set[3])
        if self.node3!=0:
            ii=-1
        elif  self.node3 not in Node_list:
            ii=len(Node_list)
            Node_list.append(self.node3)
            node_counter+=1
        else:
            ii=Node_list.index(self.node3)

        if self.node4!=0:
            jj=-1
        elif  self.node4 not in Node_list:
            jj=len(Node_list)
            Node_list.append(self.node4)
            node_counter+=1
        else:
            jj=Node_list.index(self.node4)
        
        I_list.append((self.name,exI_counter))
        V_list.append((self.name,[ii,jj]))
        exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithVCVS(self, fo):
        double_print(
            'Line#%d. The element is VCVS %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                     self.name,
                                                                                                     self.node1,
                                                                                                     self.node2,
                                                                                                     self.parameters),
            fo)


class CCCS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if Node_list.has_key(self.node3):
            mm=Node_list.get(self.node3)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node4):
            nn=Node_list.get(self.node4)
        else:
            raise NetlistParseError()

        if I_list.has_key(self.Vname):
            pp=Node_list.get(self.Vname)
        else:
            raise NetlistParseError()
            
        if pp!=-1:
            if ii!=-1:
                B[ii,pp]+=self.value
            if jj!=-1:
                B[jj,pp]-=self.value

        return (G,I,B,C,U,D)
    def getDevice(self,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+(v)[A-Za-z0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[3])
        self.Vname=self.word_set[2]
        return node_counter,V_list,Node_list,I_list,exI_counter


    def DealWithCCCS(self, fo):
        double_print(
            'Line#%d. The element is CCCS %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                     self.name,
                                                                                                     self.node1,
                                                                                                     self.node2,
                                                                                                     self.parameters),
            fo)


class VCCS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[4])
        self.node3=int(self.word_set[2])
        self.node4=int(self.word_set[3])

        if self.node3!=0:
            ii=-1
        elif  self.node3 not in Node_list:
            ii=len(Node_list)
            Node_list.append(self.node3)
            node_counter+=1
        else:
            ii=Node_list.index(self.node3)

        if self.node4!=0:
            jj=-1
        elif  self.node4 not in Node_list:
            jj=len(Node_list)
            Node_list.append(self.node4)
            node_counter+=1
        else:
            jj=Node_list.index(self.node4)
        return node_counter,V_list,Node_list,I_list,exI_counter


    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if Node_list.has_key(self.node3):
            mm=Node_list.get(self.node3)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node4):
            nn=Node_list.get(self.node4)
        else:
            raise NetlistParseError()

            
       
        if ii!=-1 and mm!=-1:
            G[ii,mm]+=self.value
        if jj!=-1 and mm!=-1:
            G[jj,mm]-=self.value
        if ii!=-1 and nn!=-1:
            G[ii,nn]-=self.value
        if jj!=-1 and nn!=-1:
            G[jj,nn]+=self.value

        return (G,I,B,C,U,D)
        
    def DealWithVCCS(self, fo):
        double_print(
            'Line#%d. The element is VCCS %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                     self.name,
                                                                                                     self.node1,
                                                                                                     self.node2,
                                                                                                     self.parameters),
            fo)


class CCVS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value

        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if Node_list.has_key(self.node3):
            mm=Node_list.get(self.node3)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node4):
            nn=Node_list.get(self.node4)
        else:
            raise NetlistParseError()

        if I_list.has_key(self.name):
            pp=Node_list.get(self.name)
        else:
            raise NetlistParseError()

        if I_list.has_key(self.Vname):
            qq=Node_list.get(self.Vname)
        else:
            raise NetlistParseError()
        if pp!=-1 and ii!=-1:    
            C[pp,ii]+=1
        if pp!=-1 and jj!=-1:
            C[pp,jj]-=1
        if ii!=-1 and pp!=-1:
            B[ii,pp]+=1
        if jj!=-1 and pp!=-1:
            B[jj,pp]-=1
        if pp!=-1 and qq!=-1:
            D[pp,qq]-=self.value


        return (G,I,B,C,U,D)

    def getDevice(self,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+(v)[A-Za-z0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[3])
        self.Vname=self.word_set[2]
        I_list.append((self.name,exI_counter))
        exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithCCVS(self, fo):
        double_print(
            'Line#%d. The element is  CCVS %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (self.counter,
                                                                                                      self.name,
                                                                                                      self.node1,
                                                                                                      self.node2,
                                                                                                      self.parameters),
            fo)


class Capacitor(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def isCL():
        return True
    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list,omega):
        #print self.value
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()

        if ii!=-1 and jj!=-1:
            G[ii, jj]-= omega*complex(0,1)*self.value
            G[jj, ii]-= omega*complex(0,1)*self.value
            G[ii, ii]+= omega*complex(0,1)*self.value
            G[jj, jj]+= omega*complex(0,1)*self.value
        elif ii==-1 and jj!=-1:
            G[jj, jj]+= omega*complex(0,1)*self.value
        elif jj==-1 and ii!=-1:
            G[ii, ii]+= omega*complex(0,1)*self.value

        return (G,I,B,C,U,D)

    def tranInit(self,G,B,C,D,U,I,Node_list, I_list):
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            kk=I_list.get(self.name)
        else:
            raise NetlistParseError()
        D[kk,kk]+=1
        return G,B,C,D,U,I
    def tranStamp(self,G,B,C,D,Node_list,I_list,h,Tran_type):
        if Tran_type=="TR":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()
            
            if ii!=-1:
            	C[kk,ii]+=2*self.value/h
            	B[ii,kk]+=1
            if jj!=-1:
            	C[kk,jj]-=2*self.value/h
            	B[jj,kk]-=1
            
            D[kk,kk]-=1
            

        elif Tran_type=="BE":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if ii!=-1 and jj!=-1:
                G[ii, jj]-= self.value/h
                G[jj, ii]-= self.value/h
                G[ii, ii]+= self.value/h
                G[jj, jj]+= self.value/h
            elif ii==-1 and jj!=-1:
                G[jj, jj]+= self.value/h
            elif jj==-1 and ii!=-1:
                G[ii, ii]+= self.value/h
        return G,B,C,D


    def tranRHS(self,U,I,I_list,h,x,node_counter,Node_list,Tran_type):
        if Tran_type=="TR":
            #print "debug",x
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()
            if ii==-1 and jj!=-1:
                v_value=-x[jj]
            elif jj==-1 and ii!=-1:
                v_value=x[ii]
            elif ii!=-1 and jj!=-1:
                v_value=x[ii]-x[jj]
            else: v_value=0

            i_value=x[node_counter+kk]
           # print 'Ikk init',I[kk]
            #print v_value,self.value,i_value
            I[kk,0]+=v_value*2.0*self.value/h+i_value
           # print v_value*2.0*self.value/h+i_value


        #print U,'debug'
        elif Tran_type=="BE":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if ii==-1 and jj!=-1:
                v_value=-x[jj]
            elif jj==-1 and ii!=-1:
                v_value=x[ii]
            elif ii!=-1 and jj!=-1:
                v_value=x[ii]-x[jj]
            else: v_value=0
            
            if ii!=-1:
                U[ii,0]+=self.value/h*v_value
            if jj!=-1:
                U[jj,0]-=self.value/h*v_value
        #print U,'debug'

        return U,I

    

    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+(e-)?[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        #self.value=eval(re.sub("(u)","e-6",word_set[2]))
        self.value=eval(self.word_set[2])
        I_list.append((self.name,exI_counter))
        exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter


    def DealWithC(self, fo):
        double_print('Line#%d. The element is  capacitance %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (
        self.counter,
        self.name, self.node1, self.node2, self.parameters), fo)


class Inductor(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isCL():
        return True

    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list,omega):
        #print self.value
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            pp=I_list.get(self.name)
        else:
            raise NetlistParseError()

        if ii!=-1:
            if pp!=-1:
                B[ii,pp]+=1
                C[pp,ii]+=1
        if jj!=-1:
            if pp!=-1:
                B[jj,pp]-=1
                C[pp,jj]-=1
        if pp!=-1:
            D[pp,pp]-=omega*complex(0,1)*self.value
        return (G,I,B,C,U,D)


    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+(k|m)?"
        isV=0
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.value=eval(self.word_set[2])
        I_list.append((self.name,exI_counter))
        exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithL(self, fo):
        double_print('Line#%d. The element is  inductance %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (
        self.counter,
        self.name, self.node1, self.node2, self.parameters), fo)

    def tranInit(self,G,B,C,D,U,I,Node_list, I_list):
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            kk=I_list.get(self.name)
        else:
            raise NetlistParseError()
        B[ii,kk]+=1
        B[jj,kk]-=1
        C[kk,ii]+=1
        C[kk,jj]-=1
        return G,B,C,D,U,I
    def tranStamp(self,G,B,C,D,Node_list,I_list,h,Tran_type):
        if Tran_type=="BE":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()
            if ii!=-1:
                B[ii,kk]+=1
                C[kk,ii]+=1
            if jj!=-1:
                B[jj,kk]-=1
                C[kk,jj]-=1
            D[kk,kk]-=self.value/h
        elif Tran_type=="TR":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()
            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()
            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()
            if ii!=-1:
                B[ii,kk]+=1
                C[kk,ii]+=1
            if jj!=-1:
                B[jj,kk]-=1
                C[kk,jj]-=1
            D[kk,kk]-=self.value*2/h

        return G,B,C,D

    def tranRHS(self,U,I,I_list,h,x,node_counter,Node_list,Tran_type):
        if Tran_type=="BE":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()

            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()

            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()

            i_value=x[kk+node_counter]
            I[kk,0]-=self.value/(h*i_value)
        elif Tran_type=="TR":
            if Node_list.has_key(self.node1):
                ii=Node_list.get(self.node1)
            else:
                raise NetlistParseError()

            if Node_list.has_key(self.node2):
                jj=Node_list.get(self.node2)
            else:
                raise NetlistParseError()

            if I_list.has_key(self.name):
                kk=I_list.get(self.name)
            else:
                raise NetlistParseError()

            if ii==-1 and jj!=-1:
                v_value=-x[jj]
            elif jj==-1 and ii!=-1:
                v_value=x[ii]
            elif ii!=-1 and jj!=-1:
                v_value=x[ii]-x[jj]
            else: v_value=0
            i_value=x[kk+node_counter]
            #print 'debug'
           
            #print v_value
            #print i_value
            #print 2.0*self.value/h*i_value-v_value
            I[kk,0]-=2.0*self.value/h*i_value+v_value

        return U,I


class Diode(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isDiode():
        return True

    def Stamp(self,G,I,B,C,U,D,V_list,I_list,Node_list):
        #print self.value
        if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if I_list.has_key(self.name):
            pp=I_list.get(self.name)
        else:
            raise NetlistParseError()

        
        return (G,I,B,C,U,D)


    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[a-zA-Z]+"
        isV=0
        self.value=0  ##to store the old voltage value
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        #I_list.append((self.name,exI_counter))
        #exI_counter+=1
        return node_counter,V_list,Node_list,I_list,exI_counter

    def DealWithD(self, fo):
        double_print('Line#%d. The element is diode %s @node1[%s] @node2[%s] and its parameters are [%s]\n' % (
        self.counter,
        self.name, self.node1, self.node2, self.parameters), fo)
    def ChangeV(self,v_value):
    	self.value=v_value
    def getV(self):
    	return self.value
    def getError(self,x,Node_list):
    	if Node_list.has_key(self.node1):
    		ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if ii!=-1 and jj!=-1:
        	v_value=x[ii]-x[jj]
        elif ii!=-1 and jj==-1:
        	v_value=x[ii]
        elif ii==-1 and jj!=-1:
        	v_value=-x[jj]
        else:
        	v_value=0
        #if self.value==0:
      #  	print "zero!!!"
       # 	sys.exit(1)
        #print 'Error',abs(v_value-self.value)
        return abs(v_value-self.value)
    def UpdateV(self,x,Node_list):
    	if Node_list.has_key(self.node1):
    		ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        if ii!=-1 and jj!=-1:
        	v_value=x[ii]-x[jj]
        elif ii!=-1 and jj==-1:
        	v_value=x[ii]
        elif ii==-1 and jj!=-1:
        	v_value=-x[jj]
        else:
        	v_value=0
       # if v_value<0:
       #     print "negtive"
       #     sys.exit(1)
        self.value=v_value
       # print 'Updated'
      #  print self.value
    def tranStamp(self,G,Node_list):
    	if Node_list.has_key(self.node1):
    		ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()
        v_value=self.value
        G0=40*math.exp(40*v_value)*(1e-14)
            
        if ii!=-1:
            G[ii,ii]+=G0
        if jj!=-1:
            G[jj,jj]+=G0
        if ii!=-1 and jj!=-1:
        	G[ii,jj]-=G0
        	G[jj,ii]-=G0
        return G

    def tranRHS(self,U,Node_list):
    	if Node_list.has_key(self.node1):
            ii=Node_list.get(self.node1)
        else:
            raise NetlistParseError()

        if Node_list.has_key(self.node2):
            jj=Node_list.get(self.node2)
        else:
            raise NetlistParseError()


        v_value=self.value
        i_value=(1e-14)*math.exp(40*v_value)-1
        G0=(1e-14)*40*math.exp(40*v_value)
        I0=i_value-G0*v_value
        if ii!=-1:
        	U[ii,0]-=I0
        if jj!=-1:
        	U[jj,0]+=I0
        return U   

class NMOS(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isMOS():
        return True
    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+"
        isV=0
        self.I=0
        
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.D=int(self.word_set[0])
        self.G=int(self.word_set[1])
        self.S=int(self.word_set[2])
        self.W=eval(self.word_set[3])
        self.L=eval(self.word_set[4])
        self.VTH=0.7
        self.K=3.835e-4
        return node_counter,V_list,Node_list,I_list,exI_counter    

    def Stamp(self,G,U,V_list,I_list,Node_list,x):
        #print self.value
        if Node_list.has_key(self.D):
            dd=Node_list.get(self.D)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.G):
            gg=Node_list.get(self.G)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.S):
            ss=I_list.get(self.S)
        else:
        	raise NetlistParseError()
        if dd!=-1 and ss!=-1:
        	vds=x[dd,0]-x[ss,0]
        elif dd==-1 and ss!=-1:
        	vds=x[ss,0]
        elif dd!=-1 and ss==-1:
        	vds=x[dd,0]
        else:
        	vds=0

        if gg!=-1 and ss!=-1:
        	vgs=x[gg,0]-x[ss,0]
        elif gg==-1 and ss!=-1:
        	vgs=x[ss,0]
        elif gg!=-1 and ss==-1:
        	vgs=x[gg,0]
        else:
        	vgs=0
        gm=0
        gds=0
        if (vgs>self.VTH ) and (vds<(vgs-self.VTH)):
        	gm=self.W/self.L*self.K*vds
        	gds=self.W/self.L*self.K*(vgs-self.VTH-vds)
        elif (vds>=(vgs-self.VTH)) and (vgs>self.VTH):
        	gds=0
        	gm=self.W/self.L*self.K*(vgs-self.VTH)
        if dd!=-1:
        	G[dd,dd]+=gds
        	if gg!=-1:
        		G[dd,gg]+=gm
        if ss!=-1:
        	G[ss,ss]+=gds+gm
        	if gg!=-1:
        		G[ss,gg]-=gm
        if dd!=-1 and ss!=-1:
        	G[dd,ss]-=gds+gm
        	G[ss,dd]-=gds

        Ids=gm*vgs+gds*vds+self.I
        U[dd,0]-=Ids
        U[ss,0]+=Ids
        Flag=1
        if abs(Ids-self.I)<0.01*self.I or abs(Ids-self.I)<0.001:
        	Flag=0
        self.I=Ids
        return G,U,Flag
        




class PMOS(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isMOS():
        return True
    def getDevice(self, b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+"
        isV=0
        
        (node_counter,V_list,Node_list) =Element.getDevice(self,isV,pat,b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)
        self.D=int(self.word_set[0])
        self.G=int(self.word_set[1])
        self.S=int(self.word_set[2])
        self.W=eval(self.word_set[3])
        self.L=eval(self.word_set[4])
        self.I=0
        self.VTH=-0.8
        self.K=7.67e-4
        return node_counter,V_list,Node_list,I_list,exI_counter    

    def Stamp(self,G,U,V_list,I_list,Node_list,x):
        #print self.value
        if Node_list.has_key(self.D):
            dd=Node_list.get(self.D)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.G):
            gg=Node_list.get(self.G)
        else:
            raise NetlistParseError()
        if Node_list.has_key(self.S):
            ss=I_list.get(self.S)
        else:
        	raise NetlistParseError()
        if dd!=-1 and ss!=-1:
        	vds=x[dd,0]-x[ss,0]
        elif dd==-1 and ss!=-1:
        	vds=x[ss,0]
        elif dd!=-1 and ss==-1:
        	vds=x[dd,0]
        else:
        	vds=0

        if gg!=-1 and ss!=-1:
        	vgs=x[gg,0]-x[ss,0]
        elif gg==-1 and ss!=-1:
        	vgs=x[ss,0]
        elif gg!=-1 and ss==-1:
        	vgs=x[gg,0]
        else:
        	vgs=0
        if (vgs>self.VTH) and (vds<(vgs-self.VTH)):
        	gm=self.W/self.L*self.K*vds
        	gds=self.W/self.L*self.K*(vgs-self.VTH-vds)
        elif (vds>=(vgs-self.VTH)) and (vgs>self.VTH):
        	gds=0
        	gm=self.W/self.L*self.K*(vgs-self.VTH)
        if dd!=-1:
        	G[dd,dd]+=gds
        	if gg!=-1:
        		G[dd,gg]+=gm
        if ss!=-1:
        	G[ss,ss]+=gds+gm
        	if gg!=-1:
        		G[ss,gg]-=gm
        if dd!=-1 and ss!=-1:
        	G[dd,ss]-=gds+gm
        	G[ss,dd]-=gds

        Ids=gm*vgs+gds*vds+self.I
        U[dd,0]-=Ids
        U[ss,0]+=Ids
        Flag=1
        if abs(Ids-self.I)<0.01*self.I or abs(Ids-self.I)<0.001:
        	Flag=0
        self.I=Ids
        return G,U,Flag