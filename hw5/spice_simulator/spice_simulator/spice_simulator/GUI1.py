from Tkinter import *
import tkFileDialog
import spice
 


__author__ = {'name' : 'Hongten',
              'mail' : 'hongtenzone@foxmail.com',
              'blog' : 'http://www.cnblogs.com/',
              'QQ': '648719819',
              'created' : '2013-09-11'}

# This program  shows how to make a typein box shadow a program variable.
flag = True
class App(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.pack()

        self.entrythingy = Entry(self)
        self.entrythingy.pack()

        self.button = Button(self, text="Uppercase The Entry",
                             command=self.openFile)
        self.button.pack()

        # here we have the text in the entry widget tied to a variable.
        # changes in the variable are echoed in the widget and vice versa.
        # Very handy.
        # there are other Variable types. See Tkinter.py for all
        # the other variable types that can be shadowed
        self.contents = StringVar()
        self.contents.set("this is a variable")
        self.entrythingy.config(textvariable=self.contents)

        # and here we get a callback when the user hits return. we could
        # make the key that triggers the callback anything we wanted to.
        # other typical options might be <Key-Tab> or <Key> (for anything)
        self.entrythingy.bind('<Key-Return>', self.print_contents1)

    def upper(self):
        # notice here, we don't actually refer to the entry box.
        # we just operate on the string variable and we
        # because it's being looked at by the entry widget, changing
        # the variable changes the entry widget display automatically.
        # the strange get/set operators are clunky, true...
        global flag
        flag = not flag
        if not flag:
            str = self.contents.get().upper()
            self.contents.set(str)
        else:
            str = self.contents.get().lower()
            self.contents.set(str)
        print('the contents is : ', self.contents.get())

    def  openFile(self):
        self.filename = tkFileDialog.askopenfilename(initialdir = 'C:/py/hw6')
        self.f=open(self.filename)
        for line in self.f.readlines():
            print line

    def print_contents1(self, event):
        print (self.filename,self.contents.get())
    def print_contents0(self, event):
        print("hi. contents of entry is now ---->", self.contents.get())

root = App()
root.master.title("Foo")

root.mainloop()