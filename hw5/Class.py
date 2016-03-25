import re
import sys
import os
import numpy as np
import scipy as sp
from scipy import sparse
from scipy.linalg import solve



class Commment:
    def __init__(self, word_set, counter):
        self.word_set = word_set
        self.counter = counter

    def DealWithComment(self, fo):
        # double_print('Comment line#%d!' % self.counter, fo)
        print_func("Line#%d. Here are the comments: " % self.counter, self.word_set, fo)

    def setAppend(self, word_set):
        self.word_set = self.word_set + word_set


class Type:
    def __init__(self, word_set, counter):
        self.word_set = word_set
        self.counter = counter

    def DealWithAnalysis(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Analysis type:%s   @line%d' % (self.word_set[0], self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)

    def setAppend(self, word_set):
        self.word_set = self.word_set + word_set


class Analysis_Type(Type):
    def __init__(self, *av):
        Type.__init__(self, *av)

    def DealWithAnalysis(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Analysis type:%s   @line%d' % (self.word_set[0], self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)


class Option_Type(Type):
    def __init__(self, *av):
        Type.__init__(self, *av)

    def DealWithOptions(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Option type   @line%d' % (self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)


class Control_Type(Type):
    def __init__(self, *av):
        Type.__init__(self, *av)

    def DealWithControl(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Control type:%s   @line%d' % (self.word_set[0], self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)


class Output_Type(Type):
    def __init__(self, *av):
        Type.__init__(self, *av)

    def DealWithOutput(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Output type:%s   @line%d' % (self.word_set[0], self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)


class Unknown_Control_Type(Type):
    def __init__(self, *av):
        Type.__init__(self, *av)

    def DealWithUnknownControl(self, fo):
        self.word_set[0] = self.word_set[0][1:]
        double_print('Unknown Control type:%s   @line%d' % (self.word_set[0], self.counter), fo)
        print_func("Parameters: ", self.word_set, fo)
