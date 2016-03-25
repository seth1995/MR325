# written by Hao Yu
# 03.08.2016
import re
import sys
import os
import numpy as np
import scipy as sp
from scipy import sparse
from scipy.linalg import solve
from device import *
from Class import *
import string
import math
import copy
import matplotlib.pyplot as plt
import Gnuplot
import string
from math	import *

class NetlistParseError(Exception):
    """Netlist parsing exception."""
    pass

def double_print(word, fo):
    # print word   #for debug
    print >> fo, word


def double_print2(word, fo):
    # print word,   #for debug
    print >> fo, word,


def validateFile(name):  # check validation
    if len(name) < 255:
        if re.match("^.+[.](SP|sp)$", name) != None:
            return 1
    return 0


def print_func(output_word, word_set, fo):
    double_print2(output_word, fo)
    del word_set[0]
    double_print2("[", fo)
    for word in word_set:
        double_print2(word, fo)
    if len(word_set) == 0:
        double_print2('No word', fo)
    double_print2("]", fo)
    double_print('\n', fo)


def parse_line(line, counter, fo,node_counter,exI_counter):
    word_set = line.split()
    num = len(word_set)
    global last_ele,acMin,acMax,ToSolveAC
    global ele_set,V_list,I_list,Node_list,CL_set,D_set,U_set,MOS_set
    global G, V,B,C,I,U
    End=0
    PlusFlag=0
    if counter == 1:
        double_print("First line:%s\n" % line, fo)
        b1stline = 1
        return  End,node_counter,exI_counter
    else:
        b1stline = 0
    if num == 0:
        return  End,node_counter,exI_counter
        # print num
    type = word_set[0]
    if re.match("^[.](end)$", type) != None:
        End=1

    elif type == '*':
        comment = Commment(word_set, counter)
        ele_set.append(comment)


    elif re.match("^[$!@#%^&()_-]", type) != None:
        double_print('Illegal line#%d' % counter, fo)
        double_print2('\n', fo)
        pass

    elif type == "+":
        if last_ele == None:  # to avoid error!
            return  End,node_counter,exI_counter
        del word_set[0]
        last_ele.setAppend(word_set)
        plusFlag=1
    #Device
    elif re.match("^r.+$", type) != None:
        ele = Resistor(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^v.+$", type) != None:
        ele = Vsrc(word_set, counter)
        ele_set.append(ele)
        U_set.append(ele)
        last_ele = ele
    elif re.match("^i.+$", type) != None:
        ele = Isrc(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^g.+$", type) != None:
        ele = VCCS(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^e.+$", type) != None:
        ele = VCVS(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^f.+$", type) != None:
        ele = CCCS(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^h.+$", type) != None:
        ele = CCVS(word_set, counter)
        ele_set.append(ele)
        last_ele = ele
    elif re.match("^c.+$", type) != None:
        ele = Capacitor(word_set, counter)
        CL_set.append(ele)
        last_ele = ele
    elif re.match("^l.+$", type) != None:
        ele = Inductor(word_set, counter)
        CL_set.append(ele)
        last_ele = ele
    elif re.match("^d.+$", type) != None:
        ele = Diode( word_set,counter)
        D_set.append(ele)
        last_ele=ele
    elif re.match("^mn.+$", type) != None:
        ele = NMOS(word_set,counter)
        MOS_set.append(ele)
        last_ele=ele
    elif re.match("^mp.+$", type) != None:
        ele = PMOS(word_set,counter)
        MOS_set.append(ele)
        last_ele=ele
    elif re.match("^[.](ac|dc|tran|op|noise)$", type) != None:
        ana = Analysis_Type(word_set, counter)
        ele_set.append(ana)
        last_ele = ana
        if type==".ac":
            acMin=eval(word_set[2])
            acMax=eval(word_set[3])
            ToSolveAC=1

    elif re.match("^[.](options)$", type) != None:
        opt = Option_Type(word_set, counter)
        ele_set.append(opt)
        last_ele = opt

    elif re.match("^[.](include|lib|param|data|alter|global|inc)$", type) != None:
        ctr = Control_Type(word_set, counter)
        ele_set.append(ctr)
        last_ele = ctr

    elif re.match("^[.](print|plot|probe|measure)$", type) != None:
        output = Output_Type(word_set, counter)
        ele_set.append(output)
        last_ele = output

    else:
        pass

    if ~PlusFlag and counter>1:
        flag1=0
        try:
            flag1=last_ele.isElement()
        except:
            flag1=0
        if flag1:
            (node_counter,V_list,Node_list,I_list,exI_counter)=last_ele.getDevice(
                b1stline,fo,node_counter,V_list,exI_counter,I_list,Node_list)

    return End,node_counter,exI_counter


def main():
    #init data
    global ele_set,V_list,I_list,Node_list,CL_set,D_set,U_set,MOS_set  #CL set for AC
    global last_ele,acMin,acMax,ToSolveAC
    global G,V,I,B,C,U
    ele_set=[]
    CL_set=[]
    D_set=[]
    U_set=[]
    MOS_set=[]
    V_list=[]
    I_list=[]
    Node_list=[]
    V = np.zeros([1, 1])
    counter = 1
    ToSolveDC=1
    ToSolveAC=0
    ToSolveTran=0
    node_counter=0
    exI_counter=0
    acMin=0
    acMax=0
    tMin=0
    tMax=6
    omega=0
    End=0
    #file_name = raw_input("What's the file name:\n")
    file_name='2diode.sp'
    while validateFile(file_name) == 0:
        file_name = raw_input("Error! What's the file name:\n")

    try:
        f = open(file_name)
    except IOError:
        print 'Fail to open %s!' % file_name
        sys.exit()
    except:
        print '\nSome error/exception occurred.'
    print 'Loading %s...\n' % file_name
    output_name = file_name.strip().split(".")
    fo = open(output_name[0] + ".txt", "wb")
    double_print("****** HW4@MR325 2015-2016  (March 9 2016)  ******", fo)

    for line in f.readlines():
        line = line.strip().lower()
        (End,node_counter,exI_counter)=parse_line(line, counter, fo,node_counter,exI_counter)
        counter += 1
        if End:
            break
    ##for Martix and dict
    G=np.zeros([node_counter,node_counter])
    B=np.zeros([node_counter,exI_counter])
    C=np.zeros([exI_counter,node_counter])
    I=np.zeros([exI_counter,1])
    U=np.zeros([node_counter,1])
    D=np.zeros([exI_counter,exI_counter])
    V_list=dict(V_list)
    I_list=dict(I_list)
    Num_list=list(range(node_counter))
    Node_list.append(0)  ##gnd's index is -1
    Num_list.append(-1)
    Node_list=dict(zip(Node_list,Num_list))


    for ele in ele_set:
        Flag=0
        try:
         Flag=ele.isElement()
        except:
            Flag=0
        if Flag:
            (G,I,B,C,U,D)=ele.Stamp(G,I,B,C,U,D,V_list,I_list,Node_list)

        #print G
        #print B
        #print C
        #print D
        #print U
        #print I

    G_dc=copy.deepcopy(G)
    I_dc=copy.deepcopy(I)
    B_dc=copy.deepcopy(B)
    C_dc=copy.deepcopy(C)
    U_dc=copy.deepcopy(U)
    D_dc=copy.deepcopy(D)



    if ToSolveDC:
        omega=0
        for CL in CL_set:
            (G,I,B,C,U,D)=CL.Stamp(G,I, B, C, U, D, V_list, I_list, Node_list, omega)  #omega=0
        Flag=1
        MAXNUM=500
        M_counter=0
        U_num=np.linspace(0, 1.7,1000)
        V1=U_set[0]
        (G,I,B,C,U,D)=V1.deStamp()
        G_DC=copy.deepcopy(G)
        I_DC=copy.deepcopy(I)
        B_DC=copy.deepcopy(B)
        C_DC=copy.deepcopy(C)
        U_DC=copy.deepcopy(U)
        D_DC=copy.deepcopy(D)
        x_=np.zeros([node_counter+exI_counter,1])
        u=[]

        for u_ in U_num:
            u.append(u_)
            V1.DCStamp(G, I, B, C, U, D, V_list, I_list, Node_list, u_)
            while Flag and M_counter<=MAXNUM:
                G=copy.deepcopy(G_DC)
                U=copy.deepcopy(U_DC)
                Flag=0
                for MOS in MOS_set:
                    (G,U,Flag1)=MOS.Stamp(G,U,V_list,I_list,Node_list,x_tmp)
                    if not Flag:
                        Flag=1
                tmp=np.column_stack((C,D))
                tmp1=np.column_stack((G,B))
                tmp=np.row_stack((tmp1,tmp))
                #print tmp
                tmp1=np.row_stack((U,I))
        #print tmp1
        #print G
        #print U

                x_tmp=np.linalg.lstsq(tmp, tmp1)
        #print x
                x_tmp=x_tmp[0]
                M_counter+=1
                if M_counter>MAXNUM:
                    print "MAXNUM reached"
                    sys.exit(1)
                x_=np.column_stack(x_,x_tmp)
            plt.plot(list(x_[1,:]),list(x_[0,:]),'-b',label =('V%s'%ii))
            plt.show()





        
    if ToSolveTran:
        step=1000
        t_list=[0]
        V_debug=[0]
        Tran_type="TR"
        
        h=float(tMax-tMin)/step

        G=copy.deepcopy(G_dc)
        I=copy.deepcopy(I_dc)
        B=copy.deepcopy(B_dc)
        C=copy.deepcopy(C_dc)
        U=copy.deepcopy(U_dc)
        D=copy.deepcopy(D_dc)
        for CL in CL_set:
            (G,B,C,D,U,I)=CL.tranInit(G,B,C,D,U,I,Node_list, I_list)
            tmp=np.column_stack((C,D))
            tmp1=np.column_stack((G,B))
            tmp=np.row_stack((tmp1,tmp))
            tmp1=np.row_stack((U,I))
            x_tmp=np.linalg.lstsq(tmp, tmp1)
            x_tran=x_tmp[0]    ##init voltage and current!
            print 'MNA',tmp
            print 'RHS',tmp1
        #print x_tran
        #sys.exit(1)

        #print 'init x',x_tran
       # x_tran=np.zeros([node_counter+exI_counter,1])
        G=copy.deepcopy(G_dc)
        I=copy.deepcopy(I_dc)
        B=copy.deepcopy(B_dc)
        C=copy.deepcopy(C_dc)
        U=copy.deepcopy(U_dc)
        D=copy.deepcopy(D_dc)
        #sys.exit(0)  ##test
        for CL in CL_set:
            (G,B,C,D)=CL.tranStamp(G, B, C, D, Node_list, I_list, h,Tran_type)
        print G,B,C,D
       # sys.exit(0)
        U=copy.deepcopy(U_dc)
        I=copy.deepcopy(I_dc)
        G_tran=copy.deepcopy(G)  ##copy G 

        hasD=1
    #    for Diode in D_set:
          #  Diode.ChangeV(1)  ##U0=1
        for Diode in D_set:
            Diode.ChangeV(0.1)  ##U0=0.1
        #print 'MNA',tmp
        #print 'RHS',tmp1
        for i in range(step):
            t_now=tMin+(1+i)*h
            t_list.append(t_now)
            #V_debug.append(5*(1-math.exp(-1*t_now)))
            #CL stamp first
            G=copy.deepcopy(G_tran)
            U=copy.deepcopy(U_dc)
            I=copy.deepcopy(I_dc)
            for CL in CL_set:
                x_now=x_tran[:,x_tran.shape[1]-1]
                (U,I)=CL.tranRHS(U, I, I_list, h, x_now, node_counter,Node_list,Tran_type)
            #print 'MNA',G,B
           # print C,D
           # print 'RHS',U,I
            
            
            #diode stmap next
            if hasD:   ##consider multiple diodes
                D_counter=0
                E_factor=0.001
                D_flag=1
                MaxNum=300    
                U_tran=copy.deepcopy(U)
                while D_flag :
                    #if i==100:
                     #   sys.exit(1)
                    
                  #  print D_counter,'debug'
                    ##init the martix
                    G=copy.deepcopy(G_tran)  
                    U=copy.deepcopy(U_tran)

                    for Diode in D_set:
                        (G)=Diode.tranStamp(G,Node_list)
                        (U)=Diode.tranRHS(U,Node_list)
                   # print 'debug'
                   # print G
                   # print U
                    #sys.exit(0)
                    tmp=np.column_stack((C,D))
                    tmp1=np.column_stack((G,B))
                    tmp=np.row_stack((tmp1,tmp))
                    tmp1=np.row_stack((U,I))
                        #      print 'RHS',tmp1
                    x_tmp=np.linalg.lstsq(tmp, tmp1)
                    x_tmp=x_tmp[0]
                    D_flag=0
                    D_counter+=1
                    for Diode in D_set:
                        deta=Diode.getError(x_tmp,Node_list)
                        v_value=Diode.getV()
                        Diode.UpdateV(x_tmp,Node_list)
                        if not(deta<abs(E_factor*v_value) or deta<1e-6):
                            D_flag=1

                    if D_counter>MaxNum:
                        print "Reached maximum num!"
                        sys.exit(1)
                    # print 'Solved X',x_tmp
                   # print 'MNA',tmp
                    #print 'RHS',tmp1
                   # if D_counter==4:
                    #    sys.exit(1)


            else:
                tmp=np.column_stack((C,D))
                tmp1=np.column_stack((G,B))

                tmp=np.row_stack((tmp1,tmp))
                tmp1=np.row_stack((U,I))
                #print 'RHS',tmp1
                x_tmp=np.linalg.solve(tmp, tmp1)

            x_tran=np.column_stack((x_tran,x_tmp))
           # print 'Solved X',x_tmp
            #print 'MNA',tmp
            #print 'RHS',tmp1


            #if i==1:
               # sys.exit(0)


      #  left = plt.subplot()
        for ii in range(node_counter):
            plt.plot(t_list,list(x_tran[ii,:]),'-b',label =('V%s'%ii))
            #plt.hold()



        plt.title("Test ")
        plt.xlabel("time(s)")
        plt.ylabel("Voltage(V)")

        plt.savefig("my.jpg")
        plt.show()
       # g = Gnuplot.Gnuplot(debug=1)
       # g.title('Tran ')
        #g.xlabel('Time (s)')
       # g.ylabel('Voltage (V)')
        #double_print2("t=",fo)
        #double_print(t_list,fo)
        #double_print2("math=",fo)
        #double_print(V_debug,fo)
        #graph=list(zip(t_list,x_tran[0,:]))
        #print x_tran
       # g.plot(graph)

    if ToSolveAC:

        G=copy.deepcopy(G_dc)
        I=copy.deepcopy(I_dc)
        B=copy.deepcopy(B_dc)
        C=copy.deepcopy(C_dc)
        U=copy.deepcopy(U_dc)
        D=copy.deepcopy(D_dc)

        N=100
        step=(acMax-acMin)/N
        omega=acMin
        omega_set=[]
        for i in range(N):
            omega=acMin+i*step
            omega_set.append(omega)
            for CL in CL_set:
                (G,I,B,C,U,D)=CL.Stamp(G,I, B, C, U, D, V_list, I_list, Node_list, omega)
            tmp=np.column_stack((C,D))
            tmp1=np.column_stack((G,B))
            tmp=np.row_stack((tmp1,tmp))
            print tmp
            tmp1=np.row_stack((U,I))
            print tmp1

            try:
                x=np.linalg.solve(tmp, tmp1)
            except np.linalg.LinAlgError:
                x=np.linalg.solve(G, U)
                x=np.row_stack(x,I)
            except:
                x=np.linalg.lstsq(tmp, tmp1)

            X_martix=np.column_stack((X_martix,x))

        #print omega_set.shape(0)
        #print X_martix.shape(0)
        for i in range(node_counter):
            plt.plot(omega_set, list(X_martix[i,1:]))      # plot a line from (0, 0) to (1, 1)
            plt.title("Test %d"%(i+1))
            plt.xlabel("omega(HZ)")
            plt.ylabel("Voltage(V)")
            plt.savefig("demo%d.jpg"%(i+1))
        for i in range(exI_counter):
            plt.plot(omega_set, list(X_martix[i,1:]))      # plot a line from (0, 0) to (1, 1)
            plt.title("Test %d"%(i+1))
            plt.xlabel("omega(HZ)")
            plt.ylabel("Current(I)")
            plt.savefig("demo%d.jpg"%(i+1))
    


    f.close()
    fo.close()
    print 'Parsing succeed!'
    raw_input()


if __name__ == '__main__':
    main()
