# written by Hao Yu
# 03.27.2016
import math
import re
import  func
import sys


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
    def deStamp(self,var):
        #print self.value
        self.value=-1*self.value
        self.Stamp(var)
        self.value=-1*self.value

    def getDevice(self,pat,var):
        Node_list=var.Node_list
        line=" ".join(self.word_set)
        #print 
        pat="^"  ##close the function
        device = re.match(pat, line)
        Error = 0
        if device == None:
                double_print("Syntax error @ line %d" % self.counter, var.fo)
                Error = 1
                raise NetlistParseError()
        else:
            self.node1 = int(self.word_set[0])
            self.node2 = int(self.word_set[1])
        #print 'Error',Error
        if Error==0:
            if self.node1==0:
                self.ii=-1
            elif  self.node1 not in Node_list:
                self.ii=len(Node_list)
                Node_list.append(self.node1)
                var.node_counter+=1
            else:
                self.ii=Node_list.index(self.node1)

            if self.node2==0:
                self.jj=-1
            elif  self.node2 not in Node_list:
                self.jj=len(Node_list)
                Node_list.append(self.node2)
                var.node_counter+=1
            else:
                self.jj=Node_list.index(self.node2)
        else:
            raise NetlistParseError('Line%d'%self.counter)
       # if isV:
        #    V_list.append((self.name,[ii,jj]))

def martixGrow(G):
    tmp = np.zeros([1, G.shape[1]])
    G = np.row_stack((G, tmp))
    tmp = np.zeros([G.shape[0], 1])
    G = np.column_stack((G, tmp))
    return G
class Resistor(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        
        #self.value=eval(re.sub("(k)","e3",word_set[2]))
        self.value=func.str_to_num(self.word_set[2])


    def Stamp(self,var):
        ii=self.ii
        jj=self.jj
        G=var.G
        if ii!=-1 and jj!=-1:
            G[ii, jj] = G[ii, jj] - 1.0 / self.value
            G[jj, ii] = G[jj, ii] - 1.0 / self.value
            G[ii, ii] = G[ii, ii] + 1.0 / self.value
            G[jj, jj] = G[jj, jj] + 1.0 / self.value
        elif ii==-1 and jj!=-1:
            G[jj, jj] = G[jj, jj] + 1.0 / self.value
        elif jj==-1 and ii!=-1:
            G[ii, ii] = G[ii, ii] + 1.0 / self.value



class Vsrc(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self,var):
        pat = "[0-9]+\s+[0-9]+\s+(dc\s+)?[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        #line=" ".join(self.word_set)
        #dc_value=re.match(pat,line)
        #dc_value=re.match("[0-9]+(k|m)?",line)
        #self.value=eval(re.sub("(k)","e3",dc_value))
        #ac_value=re.match("(ac)+\s+[0-9]+(k|m)?",line)
        #self.acMag=eval(re.sub("(k)","e3",ac_value))
        self.value=func.str_to_num(self.word_set[2])


        #self.acMag=eval(self.word_set[4])

        var.I_list.append((self.name,var.exI_counter))
        self.mm=var.exI_counter

        var.exI_counter+=1
        self.offset = 0
        self.amplitude = 0
        self.frequency = 0
        self.phase = 0
        if len(self.word_set)>3 and self.word_set[3]=="sin":
            self.offset=func.str_to_num(self.word_set[4])
            self.amplitude=func.str_to_num(self.word_set[5])
            self.frequency=func.str_to_num(self.word_set[6])
            self.phase = func.str_to_num(self.word_set[7])
            var.sin_set.append(self)
        elif len(self.word_set)>3 and self.word_set[3]=="pulse":
            self.pulse_v1=func.str_to_num(self.word_set[4])
            self.pulse_v2=func.str_to_num(self.word_set[5])
            self.pulse_td=func.str_to_num(self.word_set[6])
            self.pulse_tf=func.str_to_num(self.word_set[7])
            self.pulse_pw=func.str_to_num(self.word_set[8])
            self.pulse_per=func.str_to_num(self.word_set[9])

            #print "td",self.pulse_td
            #print "tf",self.pulse_tf
           # print "pw",self.pulse_pw
            var.pulse_set.append(self)




    def Stamp(self,var):
        #print self.value
        
        C=var.C
        B=var.B
        I=var.I
        mm=self.mm
        ii=self.ii
        jj=self.jj
        
        if ii!=-1:

            C[mm,ii]+=1
            B[ii,mm]+=1
        if jj!=-1:
            C[mm,jj]-=1
            B[jj,mm]-=1
        I[mm,0]+=self.value

    def acStamp(self,var):
        #print self.value
        I=var.I
        omega=var.omega
        mm=self.mm
        self_Omega=2*math.pi*self.frequency
        
        
        acValue=self_Omega/((1j*omega)**2+self_Omega**2)
        I[mm,0]+=acValue

    def deStamp(self, var):
        # print self.value

        C = var.C
        B = var.B
        I = var.I
        mm = self.mm
        ii = self.ii
        jj = self.jj
        if ii != -1:
            C[mm, ii] -= 1
            B[ii, mm] -= 1
        if jj != -1:
            C[mm, jj] += 1
            B[jj, mm] += 1
        I[mm, 0] -= self.value
    def SinStamp(self,var,t):
        v_value=self.value  #back up
        sin_value=self.offset+self.amplitude*math.sin(2*math.pi*t*self.frequency+self.phase)  #sin
        #print "sin_value",sin_value
        self.deStamp(var)
        self.value=sin_value  ##assign
        self.Stamp(var)  ##stamp
        self.value=v_value   ##restore
    def deSinStamp(self,var,t):
        v_value=self.value  #back up
        sin_value = self.offset+self.amplitude*math.sin(2*math.pi*t*self.frequency+self.phase)  #sin
        #print "de sin_value", sin_value
        self.deStamp(var)
        self.value=sin_value  ##assign
        self.Stamp(var)  ##stamp
        self.value=v_value   ##restore



    def PulseStamp(self,var,t):
        v_value=self.value  #back up
        t=t%self.pulse_per
        pulse_value=0  #pulse
        if (t<=self.pulse_td):
            pulse_value=t/self.pulse_td*(self.pulse_v2-self.pulse_v1)+self.pulse_v1
        elif t>self.pulse_td and t<=(self.pulse_td+self.pulse_pw):
            pulse_value=self.pulse_v2
        elif t>(self.pulse_td+self.pulse_pw) and t<=(self.pulse_td+self.pulse_pw+self.pulse_tf):
            pulse_value=self.pulse_v2-(t-self.pulse_td-self.pulse_pw)/self.pulse_tf*(self.pulse_v2-self.pulse_v1)
        else:
            pulse_value=self.pulse_v1

        #print "pulse_value",sin_value
        self.deStamp(var)
        self.value=pulse_value  ##assign
        self.Stamp(var)  ##stamp
        self.value=v_value   ##restore

    def dePulseStamp(self,var,t):
        v_value=self.value  #back up
        t=t%self.pulse_per
        pulse_value=0  #pulse
        if (t<=self.pulse_td):
            pulse_value=t/self.pulse_td*(self.pulse_v2-self.pulse_v1)+self.pulse_v1
        elif t>self.pulse_td and t<=(self.pulse_td+self.pulse_pw):
            pulse_value=self.pulse_v2
        elif t>(self.pulse_td+self.pulse_pw) and t<=(self.pulse_td+self.pulse_pw+self.pulse_tf):
            pulse_value=self.pulse_v2-(t-self.pulse_td-self.pulse_pw)/self.pulse_tf*(self.pulse_v2-self.pulse_v1)
        else:
            pulse_value=self.pulse_v1
        self.deStamp(var)
        self.value=pulse_value  ##assign
        self.Stamp(var)  ##stamp
        self.value=v_value   ##restore








class Isrc(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        self.value=func.str_to_num(self.word_set[2])


    def Stamp(self,var):
        #print self.value
        U=var.U
        ii=self.ii
        jj=self.jj


        if ii!=-1:
            U[ii,0]-=self.value
        if jj!=-1:
            U[jj,0]+=self.value


class VCVS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def Stamp(self,var):
        #print self.value
        pp=self.pp
        ii=self.ii
        jj=self.jj
        mm=self.mm
        nn=self.nn
        B=var.B
        C=var.C
        U=var.U
            
        if pp!=-1:
            if ii!=-1:
                B[ii,pp]+=1
                C[pp,ii]+=1
            if jj!=-1:
                B[jj,pp]-=1
                C[pp,jj]-=1
            if mm!=-1:
                C[pp,mm]-=self.value
            if nn!=-1:
                C[pp,nn]+=self.value

    def getDevice(self,var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        
        Node_list=var.Node_list
        I_list=var.I_list
        self.value=func.str_to_num(self.word_set[4])
        self.node3=eval(self.word_set[2])
        self.node4=eval(self.word_set[3])
        
        if self.node3==0:
            self.mm=-1
        else:
            self.mm=Node_list.index(self.node3)

        if self.node4==0:
            self.nn=-1
        else:
            self.nn=Node_list.index(self.node4)

        
        I_list.append((self.name,var.exI_counter))
        self.pp=var.exI_counter
        var.exI_counter+=1





class CCCS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def Stamp(self,var):
        #print self.value
        pp=self.pp
        ii=self.ii
        jj=self.jj
        B=var.B

        if pp!=-1:
            if ii!=-1:
                B[ii,pp]+=self.value
            if jj!=-1:
                B[jj,pp]-=self.value


    def getDevice(self,var):
        pat = "[0-9]+\s+(v)[A-Za-z0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        
        self.value=func.str_to_num(self.word_set[3])
        self.Vname=self.word_set[2]
        Node_list=var.Node_list

        if self.Vname in var.Name_set():
            ele=var.Name_set(var.Name_set.index(self.Vname))
        else:
            self.mm=-1
            self.nn=-1
            self.node3=-1
            self.node4=-1
            return
        self.node3=ele.node3
        self.node4=ele.node4
        self.mm=ele.ii
        self.nn=ele.jj

        





class VCCS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        self.value=func.str_to_num(self.word_set[4])
        self.node3=int(self.word_set[2])
        self.node4=int(self.word_set[3])
        Node_list=var.Node_list

        if self.node3!=0:
            self.ii=-1
        else:
            self.ii=Node_list.index(self.node3)

        if self.node4!=0:
            self.jj=-1
        else:
            self.jj=Node_list.index(self.node4)



    def Stamp(self,var):
        #print self.value

        ii=self.ii
        jj=self.jj
        mm=self.mm
        nn=self.nn
        G=var.G
       
        if ii!=-1 and mm!=-1:
            G[ii,mm]+=self.value
        if jj!=-1 and mm!=-1:
            G[jj,mm]-=self.value
        if ii!=-1 and nn!=-1:
            G[ii,nn]-=self.value
        if jj!=-1 and nn!=-1:
            G[jj,nn]+=self.value



class CCVS(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)

    def Stamp(self,var):
        #print self.value

        ii=self.ii
        jj=self.jj
        mm=self.mm
        nn=self.nn
        pp=self.pp
        qq=self.qq
        B=var.B
        C=var.C
        D=var.D


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


    def getDevice(self,var):
        pat = "[0-9]+\s+(v)[A-Za-z0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        Element.getDevice(self,pat,var)
        
        self.value=func.str_to_num(self.word_set[3])
        self.Vname=self.word_set[2]
        Node_list=var.Node_list

        if self.Vname in var.Name_set():
            ele=var.Name_set(var.Name_set.index(self.Vname))
        else:
            self.mm=-1
            self.nn=-1
            self.pp=-1
            self.qq=-1
            self.node3=-1
            self.node4=-1
            return
        self.node3=ele.node3
        self.node4=ele.node4
        self.mm=ele.ii
        self.nn=ele.jj
        self.qq=ele.mm
       
        
        I_list.append((self.name,var.exI_counter))
        self.pp=var.exI_counter
        var.exI_counter+=1
        
        



class  Capacitor(Element):
    def __init__(self, *av):
        Element.__init__(self, *av)
    def isCL():
        return True

    def  getLTEError(self,var,x_tran,step):
        kk=x_tran.shape[1]
       
        xn = x_tran[var.node_counter+self.mm, kk - 1]
        xn1 = x_tran[var.node_counter+self.mm, kk - 2]
        deta=abs(xn-xn1)*step/(2*self.value)

        
        
        if deta<var.LTEError:
            return 1
        else:
            return 0



    def Stamp(self,var):
        #print self.value
        ii=self.ii
        jj=self.jj
        B=var.B
        C=var.C
        D=var.D
        G=var.G
        kk=self.mm
        omega=var.omega
        """
        if ii!=-1 and jj!=-1:
            G[ii, jj]-= omega*1j*self.value
            G[jj, ii]-= omega*1j*self.value
            G[ii, ii]+= omega*1j*self.value
            G[jj, jj]+= omega*1j*self.value
        elif ii==-1 and jj!=-1:
            G[jj, jj]+= omega*1j*self.value
        elif jj==-1 and ii!=-1:
            G[ii, ii]+= omega*1j*self.value
        """
        if ii != -1 and jj != -1:

            B[ii, kk] += 1
            B[jj, kk] -= 1
            C[kk, ii] += omega*1j*self.value
            C[kk, jj] -= omega*1j*self.value
        elif ii != -1 and jj == -1:
            C[kk, ii] += omega*1j*self.value
            B[ii, kk] += 1
        elif jj != -1 and ii == -1:
            C[kk, jj] -= omega*1j*self.value
            B[jj, kk] -= 1
        D[kk,kk]-=1
    def deStamp(self,var):
        #print self.value
        ii=self.ii
        jj=self.jj
        B=var.B
        C=var.C
        D=var.D
        G=var.G
        kk=self.mm
        omega=var.omega
        """
        if ii!=-1 and jj!=-1:
            G[ii, jj]-= omega*1j*self.value
            G[jj, ii]-= omega*1j*self.value
            G[ii, ii]+= omega*1j*self.value
            G[jj, jj]+= omega*1j*self.value
        elif ii==-1 and jj!=-1:
            G[jj, jj]+= omega*1j*self.value
        elif jj==-1 and ii!=-1:
            G[ii, ii]+= omega*1j*self.value
        """
        if ii != -1 and jj != -1:

            B[ii, kk] -= 1
            B[jj, kk] += 1
            C[kk, ii] -= omega*1j*self.value
            C[kk, jj] += omega*1j*self.value
        elif ii != -1 and jj == -1:
            C[kk, ii] -= omega*1j*self.value
            B[ii, kk] -= 1
        elif jj != -1 and ii == -1:
            C[kk, jj] += omega*1j*self.value
            B[jj, kk] += 1
        D[kk,kk]+=1



    def tranInit(self,var):
        D=var.D
        mm=self.mm
        D[mm,mm]+=1
        
    def tranStamp(self,var):
        ii=self.ii
        jj=self.jj
        kk=self.mm
        h=var.tranH
        B=var.B
        C=var.C
        D=var.D
        G=var.G
        Tran_type=var.tranType
        if Tran_type=="TR":

            if ii!=-1:
                C[kk,ii]+=2*self.value/h
                B[ii,kk]+=1
            if jj!=-1:
                C[kk,jj]-=2*self.value/h
                B[jj,kk]-=1
            
            D[kk,kk]-=1
            

        elif Tran_type=="BE":
            """
            if ii!=-1 and jj!=-1:
            
                G[ii, jj]-= self.value/h
                G[jj, ii]-= self.value/h
                G[ii, ii]+= self.value/h
                G[jj, jj]+= self.value/h
            elif ii==-1 and jj!=-1:
                G[jj, jj]+= self.value/h
            elif jj==-1 and ii!=-1:
                G[ii, ii]+= self.value/h
            """
            if ii != -1 and jj != -1:

                B[ii, kk] += 1
                B[jj, kk] -= 1
                C[kk, ii] += self.value / h
                C[kk, jj] -= self.value / h
            elif ii != -1 and jj == -1:
                C[kk, ii] += self.value / h
                B[ii, kk] += 1
            elif jj != -1 and ii == -1:
                C[kk, jj] -= self.value / h
                B[jj, kk] -= 1
            D[kk,kk]-=1

 


    def tranRHS(self,var):
        ii=self.ii
        jj=self.jj
        kk=self.mm
        x=var.x
        node_counter=var.node_counter
        I=var.I
        U=var.U
        Tran_type=var.tranType
        if ii==-1 and jj!=-1:
                v_value=-x[jj]
        elif jj==-1 and ii!=-1:
                v_value=x[ii]
        elif ii!=-1 and jj!=-1:
                v_value=x[ii]-x[jj]
        else: v_value=0
        h = var.tranH
        if Tran_type=="TR":
            

            i_value=x[node_counter+kk]
           # print 'Ikk init',I[kk]
            #print v_value,self.value,i_value
            
            
            
            I[kk,0]+=v_value*2.0*self.value/var.tranH+i_value
           
           # print v_value*2.0*self.value/h+i_value


        #print U,'debug'

        elif Tran_type=="BE":
            """
            if ii!=-1:
                U[ii,0]+=self.value/h*v_value
            if jj!=-1:
                U[jj,0]-=self.value/h*v_value
            """
            I[kk,0]+=self.value*v_value/var.tranH
        #print U,'debug'

    

    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+(e-)?[0-9]+(k|m|p|f|t|u|n)?"
 
        Element.getDevice(self,pat,var)
        #self.value=eval(re.sub("(u)","e-6",word_set[2]))
        self.value=func.str_to_num(self.word_set[2])
        var.I_list.append((self.name,var.exI_counter))
        self.mm = var.exI_counter
        var.exI_counter+=1




class Inductor(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isCL():
        return True

    def  getLTEError(self,var,x_tran,step):
        kk=x_tran.shape[1]
        ii=self.ii
        jj=self.jj
        x=x_tran
        if ii==-1 and jj!=-1:
            v_value_n=-x[jj,kk - 1]
            v_value_n1=-x[jj,kk - 2]
        elif jj==-1 and ii!=-1:
            v_value_n=x[ii,kk - 1]
            v_value_n1=x[ii,kk - 2]
        elif ii!=-1 and jj!=-1:
            v_value_n=x[ii,kk - 1]-x[jj,kk - 1]
            v_value_n1=x[ii,kk - 2]-x[jj,kk - 2]
        else: 
            v_value_n=0
            v_value_n1=0

       
        
        deta=abs(v_value_n-v_value_n1)*step/(2*self.value)

        if deta<var.LTEError:
            return 1
        else:
            return 0
    def Stamp(self,var):
        #print self.value
        ii=self.ii
        jj=self.jj
        pp=self.mm
        B=var.B
        C=var.C
        D=var.D
        omega=var.omega

        if ii!=-1:
            if pp!=-1:
                B[ii,pp]+=1
                C[pp,ii]+=1
        if jj!=-1:
            if pp!=-1:
                B[jj,pp]-=1
                C[pp,jj]-=1
        if pp!=-1:
            D[pp,pp]-=omega*1j*self.value
    def deStamp(self,var):
        #print self.value
        ii=self.ii
        jj=self.jj
        pp=self.mm
        B=var.B
        C=var.C
        D=var.D
        omega=var.omega

        if ii!=-1:
            if pp!=-1:
                B[ii,pp]-=1
                C[pp,ii]-=1
        if jj!=-1:
            if pp!=-1:
                B[jj,pp]+=1
                C[pp,jj]+=1
        if pp!=-1:
            D[pp,pp]+=omega*1j*self.value
        


    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[0-9]+(k|m|p|f|t|u|n)?"
        isV=0
        Element.getDevice(self,pat,var)
        self.value=func.str_to_num(self.word_set[2])
        var.I_list.append((self.name,var.exI_counter))
        self.mm = var.exI_counter
        var.exI_counter+=1


    def tranInit(self,var):
        ii=self.ii
        jj=self.jj
        kk=self.mm
        B=var.B
        C=var.C
        if ii!=-1:
            B[ii, kk] += 1
            C[kk, ii] += 1
        if jj!=-1:
            B[jj, kk] -= 1
            C[kk, jj] -= 1

       
    def tranStamp(self,var):
        ii=self.ii
        jj=self.jj
        kk=self.mm
        B=var.B
        C=var.C
        D=var.D
        h=var.tranH
        Tran_type = var.tranType
        if Tran_type=="BE":
            if ii!=-1:
                B[ii,kk]+=1
                C[kk,ii]+=1
            if jj!=-1:
                B[jj,kk]-=1
                C[kk,jj]-=1
            D[kk,kk]-=self.value/h
        elif Tran_type=="TR":
            if ii!=-1:
                B[ii,kk]+=1
                C[kk,ii]+=1
            if jj!=-1:
                B[jj,kk]-=1
                C[kk,jj]-=1
            D[kk,kk]-=self.value*2/h

    def tranRHS(self,var):
        ii=self.ii
        jj=self.jj
        kk=self.mm
        B=var.B
        C=var.C
        D=var.D
        h=var.tranH
        i_value=var.x[kk+var.node_counter]
        I=var.I
        Tran_type = var.tranType
        x=var.x
        if Tran_type=="BE":

            I[kk,0]-=self.value/h*i_value
        elif Tran_type=="TR":
            if ii==-1 and jj!=-1:
                v_value=-x[jj]
            elif jj==-1 and ii!=-1:
                v_value=x[ii]
            elif ii!=-1 and jj!=-1:
                v_value=x[ii]-x[jj]
            else: v_value=0

            I[kk,0]-=2.0*self.value/h*i_value+v_value



class Diode(Element):
    def __init__(self, *av):
        
        Element.__init__(self, *av)
    def isDiode():
        return True

    def tranStamp(self,var):
        #print self.value
        ii=self.ii
        jj=self.jj
        G=var.G
        v_value=self.value
        #print "debug1",v_value
        #print "debug2",var.D_ISAT
        G0=40*math.exp(40*v_value)*var.D_ISAT
            
        if ii!=-1:
            G[ii,ii]+=G0
        if jj!=-1:
            G[jj,jj]+=G0
        if ii!=-1 and jj!=-1:
            G[ii,jj]-=G0
            G[jj,ii]-=G0



    def getDevice(self, var):
        pat = "[0-9]+\s+[0-9]+\s+[a-zA-Z]+"
        isV=0
        self.value=0.1  ##to store the old voltage value
        Element.getDevice(self,pat,var)
        #I_list.append((self.name,exI_counter))
        #exI_counter+=1
        
    def ChangeV(self,v_value):
        self.value=v_value

    def getError(self,var):
        Node_list=var.Node_list
        ii=self.ii
        jj=self.jj
        x=var.x
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
    def UpdateV(self,var):
        ii=self.ii
        jj=self.jj
        x=var.x
        if ii!=-1 and jj!=-1:
            v_value=x[ii]-x[jj]
        elif ii!=-1 and jj==-1:
            v_value=x[ii]
        elif ii==-1 and jj!=-1:
            v_value=-x[jj]
        else:
            v_value=0

        self.value=v_value




    def tranRHS(self,var):
        ii=self.ii
        jj=self.jj
        U=var.U

        v_value=self.value
        i_value=var.D_ISAT*math.exp(40*v_value)-1
        G0=var.D_ISAT*40*math.exp(40*v_value)
        I0=i_value-G0*v_value
        if ii!=-1:
            U[ii,0]-=I0
        if jj!=-1:
            U[jj,0]+=I0

