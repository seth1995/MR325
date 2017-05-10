# written by Hao Yu
# 03.08.2016
import re
import sys
import os
import numpy as np
import scipy as sp
from scipy import sparse
from scipy.linalg import solve
import string
import math
import copy
import matplotlib.pyplot as plt
import string
import math
import time
import cStringIO
from var import Var


class NetlistParseError(Exception):
    """Netlist parsing exception."""
    pass


def parse(netlist):
    var = Var()

    var.string2file(netlist)
    var.analysis_text()
    # for Martix and dict
    var.initMartix()

    var.makeDict()

    var.initStamp()  # stamp for the element like R
    # var.printMartix()
    # var.printGBCDUI()
    var.backMartix()

    if var.ToSolveDC:
        var.solveDC(plotFlag=1)
    if var.ToSolveTran:
        var.solveTran()

    if var.ToSolveAC:
        var.solveAC()

    # var.printMartix()
    # var.printGBCDUI()
    # var.printX()
    var.closeFile()
    result = {}
    if hasattr(var, 'voltage_tag'):
        result['voltage'] = var.voltage_tag
    if hasattr(var, 'current_tag'):
        result['current'] = var.current_tag
    if hasattr(var, 'phase_tag'):
        result['phase'] = var.phase_tag
    return result

    # print var.Node_list
    # print var.Node_list_bak


def main(fileName):
    start = time.clock()
    var = Var()
    var.openFile(fileName)

    var.output_something()
    var.analysis_text()
    # for Martix and dict
    var.initMartix()

    var.makeDict()

    var.initStamp()  # stamp for the element like R
    # var.printMartix()
    # var.printGBCDUI()
    var.backMartix()

    if var.ToSolveDC:
        var.solveDC(plotFlag=1)
    if var.ToSolveTran:
        var.solveTran()

    if var.ToSolveAC:
        var.solveAC()

    # var.printMartix()
    # var.printGBCDUI()
    # var.printX()
    var.closeFile()
    end = time.clock()
    print end - start
    # print var.Node_list
    # print var.Node_list_bak
def parse_new(netlist):
    var = Var()

    var.string2file(netlist)
    var.analysis_text()
    # for Martix and dict
    var.initMartix()

    var.makeDict()

    var.initStamp()  # stamp for the element like R
    # var.printMartix()
    # var.printGBCDUI()
    var.backMartix()

    if var.ToSolveDC:
        var.solveDC(plotFlag=1)
    if var.ToSolveTran:
        var.solveTran()

    if var.ToSolveAC:
        var.solveAC_new()

    # var.printMartix()
    # var.printGBCDUI()
    # var.printX()
    var.closeFile()
    print var.v_result
    return var.v_result


if __name__ == '__main__':
    main()
