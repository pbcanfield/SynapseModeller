import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

class SynapseUI(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)
        container = tk.Frame(self)
        self.geometry('1000x500')

        container.pack(fill=tk.BOTH,expand=True)

        self.frames = {}
        self.frames[StartPage] = StartPage(container,self)

        self.frames[StartPage].grid(row=0,column=0,sticky='nsew')
    
        self.show_frame(StartPage)

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        #Create the synapse selection system.
        self.synapse_label_text = tk.StringVar(self)
        self.synapse_label_text.set('Synapse File:')
        self.synapse_label = tk.Label(self, textvariable=self.synapse_label_text)
        self.browse_synapse_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Synapse'))

        #Create the hoc selection system.
        self.hoc_label_text = tk.StringVar(self)
        self.hoc_label_text.set('Cell Template File:')
        self.hoc_label = tk.Label(self, textvariable=self.hoc_label_text)
        self.browse_hoc_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Hoc'))

        #Page layout.    
        #3x4 (columns,rows)
    

        #Synapse selector
        self.synapse_label.grid(column=1,row=0, sticky='ne')
        self.browse_synapse_button.grid(column=2,row=0, sticky='ne')

        #HOC selector.
        self.hoc_label.grid(column=1,row=1, sticky='ne')
        self.browse_hoc_button.grid(column=2,row=1, sticky='ne')

        #Membrane potential graph.
        self.memgraph = Figure(figsize=(5,2), dpi=100)
        self.memvtime = self.memgraph.add_subplot(111)
        self.memvtime.plot([1,2,3,4],[5,3,1,4])

        memcanvas = FigureCanvasTkAgg(self.memgraph,self)
        memcanvas.draw()
        memcanvas.get_tk_widget().grid(column = 0, row = 1)

        #Injection graph
        self.injgraph = Figure(figsize=(5,2), dpi=100)
        self.injvtime = self.injgraph.add_subplot(111)
        self.injvtime.plot([1,2,3,4],[1,2,3,4])

        injcanvas = FigureCanvasTkAgg(self.injgraph,self)
        injcanvas.draw()
        injcanvas.get_tk_widget().grid(column = 0, row = 3)
        
        #The matplotlib toolbar needs to be packed in and cannout use the grid geometry
        #manager. To fix this, create an empty frame and put the
        #stuff on this frame and pack it in. Then display the frame on the grid.    
        memtoolbar_frame = tk.Frame(master=self)
        memtoolbar_frame.grid(column=0,row=0,sticky='w')
        memtoolbar = NavigationToolbar2Tk(memcanvas,memtoolbar_frame)
        memtoolbar.update()

        injtoolbar_frame = tk.Frame(master=self)
        injtoolbar_frame.grid(column=0,row=2,sticky='w')
        injtoolbar = NavigationToolbar2Tk(injcanvas,injtoolbar_frame)
        injtoolbar.update()


    def browseFiles(self,file_type):
        file_directory = filedialog.askopenfilename(initialdir = '.', 
                                                    title= 'Select a ' + file_type + ' file.',
                                                    filetypes = (('JSON files','*.json'),
                                                                ('HOC files', '*.hoc')))
        
        #Handle a closing event.
        if type(file_directory) != str:
            return

        #check if its a synapse or hoc file and update accourdingly.
        if file_type == 'Synapse':
            self.synapse_dir = file_directory

            #Get just the file name, this is probably really terrible but it works :/
            fileName = file_directory[::-1].split('/',1)[0][::-1]

            self.synapse_label_text.set('Synapse File: ' + fileName)
        elif file_type == 'Hoc':
            self.hoc_dir = file_directory

            fileName = file_directory[::-1].split('/',1)[0][::-1]

            self.hoc_label_text.set('Cell Template File: ' + fileName)


#class ParameterPanel:
