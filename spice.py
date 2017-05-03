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
from var import Var


class NetlistParseError(Exception):
    """Netlist parsing exception."""
    pass


def main(fileName):
    start = time.clock()
    # file_name = raw_input("What's the file name:\n")
    # while validateFile(file_name) == 0:
    #   file_name = raw_input("Error! What's the file name:\n")
    var = Var()
    var.openFile(fileName)

    var.output_something()
    var.analysis_text()
    ##for Martix and dict
    var.initMartix()


    var.makeDict()

    var.initStamp()  ##stamp for the element like R
    # var.printMartix()
    # var.printGBCDUI()
    var.backMartix()

    if var.ToSolveDC:
        var.solveDC(plotFlag=1)
    if var.ToSolveTran:
        var.solveTran()

    if var.ToSolveAC:
        var.solveAC()

    var.printMartix()
    var.printGBCDUI()
    var.printX()
    var.closeFile()
    end=time.clock()
    print end-start
    print var.Node_list
    print var.Node_list_bak


if __name__ == '__main__':
    main()
