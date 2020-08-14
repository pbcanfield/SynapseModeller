import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import numpy as np

from sys import platform
import os

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

    def set_simulator(self, sim):
        self.frames[StartPage].simulator = sim 

    def show_frame(self, controller):
        frame = self.frames[controller]
        frame.tkraise()


class StartPage(tk.Frame):

    #The simulator.
    simulator = None

    #Synapse label and button.
    synapse_label_text = None
    synapse_label = None
    browse_synapse_button = None
    synapse_dir = None

    #Cell label and button
    hoc_label_text = None
    hoc_label = None
    browse_hoc_button = None
    hoc_dir = None

    #Mechanism label and button
    mech_label_text = None
    mech_label = None
    browse_mech_button = None
    mech_dir = None

    #Synapse mod label and button
    mod_label_text = None
    mod_label = None
    browse_mod_button = None
    mod_dir = None

    #Canvases for both graphs
    injcanvas = None
    memcanvas = None

    #Create the run button.
    run_button = None

    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)

        #Create the synapse selection system.
        self.synapse_label_text = tk.StringVar(self)
        self.synapse_label_text.set('Synapse template file:')
        self.synapse_label = tk.Label(self, textvariable=self.synapse_label_text)
        self.browse_synapse_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Synapse'))
 
        #Create the hoc selection system.
        self.hoc_label_text = tk.StringVar(self)
        self.hoc_label_text.set('Cell Template File:')
        self.hoc_label = tk.Label(self, textvariable=self.hoc_label_text)
        self.browse_hoc_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Hoc'))

        #Create the mechanism selection system.
        self.mech_label_text = tk.StringVar(self)
        self.mech_label_text.set('Mechanism dir/file:')
        self.mech_label = tk.Label(self, textvariable=self.mech_label_text)
        self.browse_mech_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Mech'))

        #Create the synapse mod system.
        self.mod_label_text = tk.StringVar(self)
        self.mod_label_text.set('Synapse mod file:')
        self.mod_label = tk.Label(self, textvariable=self.mod_label_text)
        self.browse_mod_button = tk.Button(self, text= 'Browse', command=lambda: self.browseFiles('Mod'))

        #Page layout.    
        #3x4 (columns,rows)
    
        #Synapse selector
        self.synapse_label.grid(column=1,row=0, sticky='ne')
        self.browse_synapse_button.grid(column=2,row=0, sticky='ne')

        #HOC selector.
        self.hoc_label.grid(column=1,row=1, sticky='ne')
        self.browse_hoc_button.grid(column=2,row=1, sticky='ne')

        #Mechanism selector.
        self.mech_label.grid(column=1,row=2, sticky='ne')
        self.browse_mech_button.grid(column=2,row=2, sticky='ne')

        #Synapse mod selector.
        self.mod_label.grid(column=1,row=3, sticky='ne')
        self.browse_mod_button.grid(column=2,row=3, sticky='ne')

        #Membrane potential graph.
        self.memgraph = Figure(figsize=(5,2), dpi=100)
        self.memvtime = self.memgraph.add_subplot(111)

        #Create the canvas for the membrane vs time graph.
        self.memcanvas = FigureCanvasTkAgg(self.memgraph,self)
        self.memcanvas.draw()
        self.memcanvas.get_tk_widget().grid(column = 0, row = 1)

        #Injection graph
        self.injgraph = Figure(figsize=(5,2), dpi=100)
        self.injvtime = self.injgraph.add_subplot(111)

        #Create the canvas for the current injection vs time graph.
        self.injcanvas = FigureCanvasTkAgg(self.injgraph,self)
        self.injcanvas.draw()
        self.injcanvas.get_tk_widget().grid(column = 0, row = 3)
        
        #The matplotlib toolbar needs to be packed in and cannout use the grid geometry
        #manager. To fix this, create an empty frame and put the
        #stuff on this frame and pack it in. Then display the frame on the grid.    
        memtoolbar_frame = tk.Frame(master=self)
        memtoolbar_frame.grid(column=0,row=0,sticky='w')
        memtoolbar = NavigationToolbar2Tk(self.memcanvas,memtoolbar_frame)
        memtoolbar.update()

        injtoolbar_frame = tk.Frame(master=self)
        injtoolbar_frame.grid(column=0,row=2,sticky='w')
        injtoolbar = NavigationToolbar2Tk(self.injcanvas,injtoolbar_frame)
        injtoolbar.update()

        #Add in the parameter panel.
        panel = ParameterPanel(self)
        panel.grid(column=3, row=0, sticky='nw')
        panel.update()

    def browseFiles(self,file_type):
        
        file_directory = None
        if file_type == 'Synapse':
            file_directory = filedialog.askopenfilename(initialdir = '.', 
                                                        title= 'Select a synapse template file.',
                                                        filetypes = [('JSON files','*.json')])
        elif file_type == 'Hoc':
            file_directory = filedialog.askopenfilename(initialdir = '.', 
                                                        title= 'Select a cell template file.',
                                                        filetypes = [('HOC files', '*.hoc')])
        elif file_type == 'Mech':
            if platform == 'linux' or platform == 'linux2' or platform == 'darwin':
                file_directory = filedialog.askdirectory(initialdir = '.', 
                                                            title= 'Select the compiled mechanism directory.')
            else:
                file_directory = filedialog.askopenfilename(initialdir = '.', 
                                                            title= 'Select the mechanism dll.',
                                                            filetypes = [('DLL files', '*.dll')])
        elif file_type == 'Mod':
            file_directory = filedialog.askopenfilename(initialdir = '.', 
                                                        title= 'Select a synapse mod file.',
                                                        filetypes = [('MOD files', '*.mod')])
        

        #Handle a closing event.
        if type(file_directory) != str:
            return

        #Get just the file name, this is probably really terrible but it works :/
        fileName = file_directory[::-1].split('/',1)[0][::-1]

        #check if its a synapse or hoc file and update accourdingly.
        if file_type == 'Synapse':
            self.synapse_dir = file_directory
            self.synapse_label_text.set('Synapse template file: ' + fileName)

        elif file_type == 'Hoc':
            self.hoc_dir = file_directory
            self.hoc_label_text.set('Cell template file: ' + fileName)
        
        elif file_type == 'Mech':
            self.mech_dir = file_directory
            self.mech_label_text.set('mechanism dir/file: ' + fileName)

        elif file_type == 'Mod':
            self.mod_dir = file_directory
            self.mod_label_text.set('Synapse file: ' + fileName)

    def update(self):
        time = self.simulator.get_time()
        self.memvtime.plot(time,self.simulator.get_membrane())
        
        for i in range(self.simulator.num_currents):
            self.injvtime.plot(time,self.simulator.get_synapse_current(i))
        
        #Redraw both graphs.
        self.memcanvas.draw()
        self.injcanvas.draw()


class ParameterPanel(tk.Frame):

    parent_ui = None
    run_button = None

    #Stores the parameters that can be changed in the synapse file.
    parameters = {}

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.parent_ui = parent

        #Create run button.
        self.run_button = tk.Button(self, text='Run', command=self.run_simulation)
        self.run_button.pack()

    
    def run_simulation(self):

        #Check that each directory has been selected properly.
        if self.parent_ui.synapse_dir == None or \
           self.parent_ui.hoc_dir == None or     \
           self.parent_ui.mech_dir == None or    \
           self.parent_ui.mod_dir == None:
            return


        #Chech if the simulator has already been initialized, if not initialize it
        #then run.
      
        self.parent_ui.simulator.set_parameters(self.parent_ui.hoc_dir,
                                                self.parent_ui.mech_dir,
                                                self.parent_ui.synapse_dir,
                                                self.parent_ui.mod_dir)

        

        #Now run the simulation.
        self.parent_ui.simulator.generate_core_simulator('template.tem')
        self.parent_ui.simulator.load_core()
        self.parent_ui.simulator.run_simulation()
        self.parent_ui.simulator.clean_up()

        #Now update all the graphics.
        self.parent_ui.update()



