import re
from normal_device import *
import  matplotlib.pyplot as plt
from mos import NMOS
from mos import  PMOS
import numpy as np
from cStringIO import StringIO



def str_to_num(str):
    str = re.sub('[k]', 'e3', str)
    str = re.sub('[tT]', 'e12', str)
    str = re.sub('[uU]', 'e-6', str)
    str = re.sub('[nN]', 'e-9', str)
    str = re.sub('[pP]', 'e-12', str)
    str = re.sub('[m]', 'e-3', str)
    str = re.sub('(MEG)', 'e6', str)

    # print str
    num = eval(str)
    return num


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


def parse_line(line, var):
    word_set = line.split()
    num = len(word_set)
    var.End = 0
    PlusFlag = 0
    fo = var.fo
    if var.counter == 1:
        double_print("First line:%s\n" % line, fo)  ##the first line?
        b1stline = 1
        return
    else:
        b1stline = 0

    if num == 0:
        return
        # print num
    Type = word_set[0].lower()
    if re.match("^[.](end)$", Type) != None:
        var.End = 1

    elif Type == '*':
        return

    elif re.match("^[$!@#%^&()_-]", Type) != None:
        double_print('Illegal line#%d' % var.counter, fo)
        double_print2('\n', fo)


    elif Type == "+":
        if last_ele == None:  # to avoid error!
            return
        del word_set[0]
        var.last_ele.setAppend(word_set)
        PlusFlag = 1
    # Device
    elif re.match("^r.+$", Type) != None:
        ele = Resistor(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^v.+$", Type) != None:

        ele = Vsrc(word_set, var.counter)

        var.ele_set.append(ele)
        var.U_set.append(ele)
        var.last_ele = ele

    elif re.match("^i.+$", Type) != None:
        ele = Isrc(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^g.+$", Type) != None:
        ele = VCCS(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^e.+$", Type) != None:
        ele = VCVS(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^f.+$", Type) != None:
        ele = CCCS(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^h.+$", Type) != None:
        ele = CCVS(word_set, var.counter)
        var.ele_set.append(ele)
        var.last_ele = ele
    elif re.match("^c.+$", Type) != None:
        ele = Capacitor(word_set, var.counter)
        var.CL_set.append(ele)
        var.last_ele = ele
    elif re.match("^l.+$", Type) != None:
        ele = Inductor(word_set, var.counter)
        var.CL_set.append(ele)
        var.last_ele = ele
    elif re.match("^d.+$", Type) != None:
        ele = Diode(word_set, var.counter)
        var.D_set.append(ele)
        var.last_ele = ele
    elif re.match("^mn.+$", Type) != None:
        ele = NMOS(word_set, var.counter)
        var.MOS_set.append(ele)
        var.last_ele = ele
    elif re.match("^mp.+$", Type) != None:
        ele = PMOS(word_set, var.counter)
        var.MOS_set.append(ele)
        var.last_ele = ele
    elif re.match("^[.](ac|dc|tran|op|noise)$", Type) != None:
        if Type == ".ac":
            var.AC_type = word_set[1]
            var.acPoint = str_to_num(word_set[2])
            var.acMin =str_to_num(word_set[3])
            var.acMax = str_to_num(word_set[4])
            var.ToSolveAC = 1
        elif Type == ".dc":
            var.DC_target = word_set[1]
            var.DC_Min = str_to_num(word_set[2])
            var.DC_Max = str_to_num(word_set[3])
            var.DC_h = str_to_num(word_set[4])
            var.ToSolveDC = 1
        elif Type == ".tran":
            var.tranType = word_set[1]
            var.tranMin = str_to_num(word_set[2])
            var.tranMax = str_to_num(word_set[3])
            var.tranH = str_to_num(word_set[4])
            var.ToSolveTran = 1

    elif re.match("^[.](options)$", Type) != None:
        return

    elif re.match("^[.](include|lib|param|data|alter|global|inc)$", Type) != None:
        return

    elif re.match("^[.](print|plot|probe|measure)$", Type) != None:
        return

    if ~PlusFlag and var.counter > 1:
        flag1 = 0
        try:
            flag1 = var.last_ele.isElement()
        except:
            flag1 = 0
        if flag1 and var.last_ele != None:
            var.last_ele.getDevice(var)
            var.Name_set.append((var.last_ele.name, var.last_ele))
            var.last_ele = None


def plotV(var, t, x):

    for ii in range(var.node_counter):
        plt.figure()
        plt.plot(t, list(x[ii, :]),label="V%d"%var.Node_list_bak[ii])
        plt.title("V%d"%var.Node_list_bak[ii])
        plt.xlabel("time(s)")
        plt.ylabel("Voltage(V)")
        plt.legend()



    #plt.title("Test ")
    #plt.xlabel("time(s)")
    #plt.ylabel("Voltage(V)")
    #plt.legend()

    plt.savefig("vol.jpg")

    plt.show()

    for ii in range(var.exI_counter):

        plt.plot(t, list(x[ii+var.node_counter, :]), '*', label=('I%s' % ii))
    plt.title("Test ")
    plt.xlabel("time(s)")
    plt.ylabel("Current(A)")

    plt.savefig("cur.jpg")
    plt.show()

def plotV_AC(var, t, x):
    io=StringIO()
    plt.figure()
    #voltage image
    plt.title("Voltage")
    plt.xlabel("frequecy(HZ)")
    plt.ylabel("Voltage(V)")
    for ii in range(var.node_counter):
        pltac_temp=np.divide(x[ii, :],x[0, :])
        plt.semilogx(t, list(abs(pltac_temp)),label="V%d"%var.Node_list_bak[ii])
    plt.legend()
    plt.savefig(io,format="png")
    voltage_tag='<img src="data:image/png;base64,%s"/>'% io.getvalue().encode("base64").strip()
    print voltage_tag
    #phase image
    plt.figure()
    plt.title("Phase")
    plt.xlabel("frequecy(HZ)")
    plt.ylabel("Phase(degs)")

    for ii in range(var.node_counter):
        pltac_temp=np.divide(x[ii, :],x[0, :])
        x_temp=np.arctan2(pltac_temp.imag,pltac_temp.real)
        x_temp=np.divide(x_temp,math.pi/180)
        plt.semilogx(t, list(x_temp),label="V%d"%var.Node_list_bak[ii])
    plt.legend()
    plt.savefig(io,format="png")
    phase_tag='<img src="data:image/png;base64,%s"/>'% io.getvalue().encode("base64").strip()

    #current image
    plt.figure()
    plt.title("Current")
    plt.xlabel("frequecy(HZ)")
    plt.ylabel("Current(A)")
    for ii in range(var.exI_counter):
        plt.semilogx(t, list(x[ii+var.node_counter, :]),  label=('I%s' % ii))
    plt.legend()

    #plt.savefig("cur.jpg")
    plt.savefig(io,format="png")
    current_tag='<img src="data:image/png;base64,%s"/>'% io.getvalue().encode("base64").strip()
