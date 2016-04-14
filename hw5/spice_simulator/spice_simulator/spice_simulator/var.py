import numpy as np
import copy
import math
import matplotlib.pyplot as plt
from func import double_print
from func import double_print2
from func import  parse_line
from func import  plotV
from func import  plotV_AC
import sys
class Var:
    def __init__(self):
        ##set and list
        self.ele_set=[]
        self.CL_set=[]
        self.D_set=[]
        self.U_set=[]
        self.MOS_set=[]
        self.V_list=[]
        self.I_list=[]
        self.Node_list=[]
        self.Name_set=[]  ##store element's name
        self.sin_set=[]
        self.pulse_set=[]
        #counter
        self.counter=1
        self.node_counter=0
        self.exI_counter=0
        ##Flag
        self.ToSolveDC=0
        self.ToSolveAC=0
        self.ToSolveTran=0
        #ac time parameters
        self.acMin=0
        self.acMax=0
        self.acPoint=0
        self.acType="DEC"
        #tran time parameters
        self.tranMin=0
        self.tranMax=0
        self.tranH=0
        self.tranType="TR"
        self.LTEError=1e-5

        #DC
        self.DC_Min=0
        self.DC_Max=0
        self.DC_h=0
        self.DC_target="NONE"
        #ac's omega
        self.omega=0
        #end flag
        self.End=0
        self.file_name='mos.sp'
        #for diode
        self.D_factor=0.001
        self.D_maxNum=500
        self.D_abError=1e-6
        self.D_ISAT=1e-14

        self.MOS_factor=1e-3
        self.MOS_maxNum=500
        self.MOS_abError=1e-6

        self.controlFlag=0
        

        
    def openFile(self,fileName):
        self.file_name=fileName
        """
        try:
            self.f = open("./sp/"+self.file_name)
        except IOError:
            print 'Fail to open %s!' % self.file_name
            sys.exit(1)
        except:
            print '\nSome error/exception occurred.'
            print 'Loading %s...\n' % self.file_name
            """
        self.f = open(self.file_name)

    def closeFile(self):
        self.fo.close()
        self.f.close()
        print 'Parsing succeed'



    def output_something(self):
        output_name = self.file_name.strip().split(".")
        self.fo = open("%s_output.txt"%self.file_name, "wb")
        double_print("****** HW6@MR325 2015-2016  (March 27 2016)  ******", self.fo)
        

    def analysis_text(self):

        for line in self.f.readlines():
            line = line.strip()
            parse_line(line,self)
            self.counter += 1

            if self.End:
                break


    def initMartix(self):
        if self.ToSolveAC:
            self.G=np.zeros([self.node_counter,self.node_counter],dtype=complex )
            self.B=np.zeros([self.node_counter,self.exI_counter],dtype=complex )
            self.C=np.zeros([self.exI_counter,self.node_counter],dtype=complex )
            self.I=np.zeros([self.exI_counter,1],dtype=complex )
            self.U=np.zeros([self.node_counter,1],dtype=complex)
            self.D=np.zeros([self.exI_counter,self.exI_counter],dtype=complex )
        else:
            self.G=np.zeros([self.node_counter,self.node_counter] )
            self.B=np.zeros([self.node_counter,self.exI_counter])
            self.C=np.zeros([self.exI_counter,self.node_counter])
            self.I=np.zeros([self.exI_counter,1])
            self.U=np.zeros([self.node_counter,1])
            self.D=np.zeros([self.exI_counter,self.exI_counter] )
    def makeDict(self):
        self.V_list=dict(self.V_list)
        self.I_list=dict(self.I_list)
        self.Num_list=list(range(self.node_counter))
        self.Node_list.append(0)  ##gnd's index is -1
        self.Num_list.append(-1)
        self.Node_list_bak=copy.deepcopy(self.Node_list)
        self.Node_list=dict(zip(self.Node_list,self.Num_list))
        self.Name_set=dict(self.Name_set)
    def printGBCDUI(self):
        print "G",self.G
        print "B",self.B
        print "C",self.C
        print "D",self.D
        print "U",self.U
        print "I",self.I
    def printX(self):
        print "x",self.x
    def initStamp(self):
        for ele in self.ele_set:
            Flag=0

            try:
                Flag=ele.isElement()
            except:
                Flag=0
            if Flag:

                ele.Stamp(self)


    def backMartix(self):
        self.G_bak=copy.deepcopy(self.G)
        self.I_bak=copy.deepcopy(self.I)
        self.B_bak=copy.deepcopy(self.B)
        self.C_bak=copy.deepcopy(self.C)
        self.U_bak=copy.deepcopy(self.U)
        self.D_bak=copy.deepcopy(self.D)
    def restoreMartix(self):
        self.G=copy.deepcopy(self.G_bak)
        self.I=copy.deepcopy(self.I_bak)
        self.B=copy.deepcopy(self.B_bak)
        self.C=copy.deepcopy(self.C_bak)
        self.U=copy.deepcopy(self.U_bak)
        self.D=copy.deepcopy(self.D_bak)
    def solveMartix(self):
        MNA1=np.column_stack((self.C,self.D))
        MNA2=np.column_stack((self.G,self.B))
        MNA=np.row_stack((MNA2,MNA1))
        RHS=np.row_stack((self.U,self.I))
        x=np.linalg.lstsq(MNA, RHS)
        self.x=x[0]
        #x=np.linalg.solve(MNA,RHS)
       # print "MNA",MNA
       # print "RHS",RHS
    def printMartix(self):
        MNA1 = np.column_stack((self.C, self.D))
        MNA2 = np.column_stack((self.G, self.B))
        MNA = np.row_stack((MNA2, MNA1))
        RHS = np.row_stack((self.U, self.I))
        print "MNA", MNA
        print "RHS", RHS
    def iterator_MOS(self):
        MOS_counter = 0

        MOS_flag = 1

        self.plot_set = np.zeros([self.node_counter + self.exI_counter, 1])

        self.U_mos = copy.deepcopy(self.U)

        self.G_mos = copy.deepcopy(self.G)

        while MOS_flag:

            self.G = copy.deepcopy(self.G_mos)

            self.U = copy.deepcopy(self.U_mos)

            for Mos in self.MOS_set:
                Mos.Stamp(self)

                    # to get x

            self.solveMartix()
            self.plot_set=np.column_stack((self.plot_set,self.x))

            MOS_flag = 0

            MOS_counter += 1

            for Mos in self.MOS_set:

                #Mos.UpdateI(self)
                #MOS can  update V while stamping

                if not Mos.ErrorOK(self):
                    MOS_flag = 1

            if MOS_counter > self.MOS_maxNum:
                print "Reached maximum num"
                plotV(self,range(MOS_counter+1),self.plot_set)

                sys.exit(1)
            for MOS in self.MOS_set:
                MOS.getVgs(self)
                MOS.getVds(self)


        
    def iterator_DIODE(self):
        D_counter=0
        D_flag=1
        self.plot_set=np.zeros([self.node_counter+self.exI_counter,1])
        self.U_diode=copy.deepcopy(self.U)
        self.G_diode=copy.deepcopy(self.G)

        while D_flag:
            self.G=copy.deepcopy(self.G_diode)
            self.U=copy.deepcopy(self.U_diode)

            for Diode in self.D_set:
                Diode.tranStamp(self)
                Diode.tranRHS(self)
            #to get x
            self.solveMartix()

            D_flag=0
            D_counter+=1

            for Diode in self.D_set:
                deta=Diode.getError(self)
                v_value=Diode.value
                Diode.UpdateV(self)

                if not (deta <self.D_abError):
                    D_flag=1
            if D_counter>self.D_maxNum:
                print "Reached maximum num"
                plotV(self,range(D_counter+1),self.plot_set)
                sys.exit(1)
            self.plot_set=np.column_stack((self.plot_set,self.x))


    def solveDC(self,plotFlag):
        dc_list = [0]
        self.omega=0
        

        if not self.DC_h==0:
            step=int((self.DC_Max-self.DC_Min)/self.DC_h)
            if (self.DC_h*step)<(self.DC_Max-self.DC_Min):
                step+=1
        else:
            step=0
        
        if not self.DC_target=="NONE":
            for CL in self.CL_set:
            #CL.tranInit(self)
                CL.Stamp(self)
            if not self.Name_set.has_key(self.DC_target):
                print "DC target do not exist!"
                sys.exit(1)
            self.DC_Ele=self.Name_set.get(self.DC_target)

            self.DC_Ele.deStamp(self)
            self.backMartix()
            x_dc = np.zeros((self.node_counter + self.exI_counter, 1))
            self.x = np.zeros((self.node_counter + self.exI_counter, 1))

            
            for i in range(step+1):
                self.restoreMartix()
                self.DC_Ele.value=self.DC_Min+i*self.DC_h
                dc_list.append(self.DC_Ele.value)
                self.DC_Ele.Stamp(self)


                if len(self.D_set)!=0:
                    self.iterator_DIODE()
                elif len(self.MOS_set)!=0:
                    self.iterator_MOS()
                else:
                    self.solveMartix()
                x_dc=np.column_stack((x_dc,self.x))
            if plotFlag:
                plotV(self,dc_list,x_dc)
        else:
            if len(self.D_set)!=0:
                    self.iterator_DIODE()
            elif len(self.MOS_set)!=0:
                self.iterator_MOS()
            else:
                self.solveMartix()
            
          




    def solveTran(self):
        t_list=[0]
        step=int((self.tranMax-self.tranMin)/self.tranH)
        self.restoreMartix()
        t_now=self.tranMin

        x_tran=np.zeros((self.node_counter+self.exI_counter,1))
        self.x=np.zeros((self.node_counter+self.exI_counter,1))

        #self.restoreMartix()

        #for CL in self.CL_set:
         #   CL.tranStamp(self)
        ##restore U,I
        self.U=copy.deepcopy(self.U_bak)
        self.I=copy.deepcopy(self.I_bak)
        ##g,b,c,d CL stamped
        self.G_tran=copy.deepcopy(self.G)
        self.B_tran = copy.deepcopy(self.B)
        self.C_tran = copy.deepcopy(self.C)
        self.D_tran = copy.deepcopy(self.D)
        ##if has D

        while t_now<self.tranMax:
            self.G=copy.deepcopy(self.G_tran)
            self.B = copy.deepcopy(self.B_tran)
            self.C = copy.deepcopy(self.C_tran)
            self.D= copy.deepcopy(self.D_tran)
            for CL in self.CL_set:
                CL.tranStamp(self)
            
            t_now=t_now+self.tranH
            t_list.append(t_now)
            
            #restore G,U,I
           # self.G=copy.deepcopy(self.G_tran)
            ## RESTORE U I for CL
            self.U=copy.deepcopy(self.U_bak)
            self.I=copy.deepcopy(self.I_bak)

            for CL in self.CL_set:
                CL.tranRHS(self)
            for Vsin in  self.sin_set:
                Vsin.SinStamp(self,t_now)
            for Vpulse in  self.pulse_set:
                Vpulse.PulseStamp(self,t_now)


            if len(self.D_set)!=0:
                self.iterator_DIODE()

            elif len(self.MOS_set) != 0:

                self.iterator_MOS()
            else:
                self.solveMartix()

            x_tran=np.column_stack((x_tran,self.x))
            #for Vsin in  self.sin_set:
             #   Vsin.deSinStamp(self,t_now)
            LTE_FLAG=0
            step_now=self.tranH
            for CL in self.CL_set:
                LTE_FLAG=CL.getLTEError(self,x_tran,step_now)
                if self.controlFlag:
                    if  LTE_FLAG:
                        self.tranH=self.tranH*1.25
                    else:
                        self.tranH=self.tranH*0.5


        plotV(self,t_list,x_tran)

    def solveAC(self):
        
        self.ac_set=[]


        #  establish ac_set
        if self.acType=="DEC":
            step=10**(1.0/self.acPoint)
            ac_temp=self.acMin
            self.ac_set.append(ac_temp)
            while ac_temp<self.acMax:
                ac_temp*=step
                self.ac_set.append(ac_temp)
                
        ac_num=len(self.ac_set)
        if not len(self.MOS_set)==0:
            self.solveDC(plotFlag=0)
            
        self.backMartix()
        
        for i in range(ac_num):
            self.restoreMartix()
            self.omega=self.ac_set[i]*math.pi*2   #note 2pi!
            
            
            for CL in self.CL_set:
                CL.Stamp(self)
            if not len(self.sin_set)==0:
                for Vsin in self.sin_set:
                    Vsin.acStamp(self)

            self.solveMartix()
            if i==0:
                x_ac=copy.deepcopy(self.x)
            else:
                x_ac=np.column_stack((x_ac,self.x))

        plotV_AC(self,self.ac_set,x_ac)




































