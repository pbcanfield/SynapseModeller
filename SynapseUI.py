import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np
import re

from sys import platform
import os

class SynapseUI(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self,*args,**kwargs)

    def initialize(self, simulator):
        container = tk.Frame(self)
        self.geometry('1150x650')
        container.pack(fill=tk.BOTH,expand=True)

        self.frames = {}
        self.frames[StartPage] = StartPage(container,self, simulator)
        self.frames[StartPage].grid(row=0,column=0,sticky='nsew')
    
        self.show_frame(StartPage)
        

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
    synapse_dir = ''

    #Cell label and button
    hoc_label_text = None
    hoc_label = None
    browse_hoc_button = None
    hoc_dir = ''

    #Mechanism label and button
    mech_label_text = None
    mech_label = None
    browse_mech_button = None
    mech_dir = ''

    #Synapse mod label and button
    mod_label_text = None
    mod_label = None
    browse_mod_button = None
    mod_dir = ''

    #Canvases for both graphs
    injcanvas = None
    memcanvas = None

    #lines for each graph.
    memline = None
    timeline = None
    currentline = []

    #Create the parameter panel.
    panel = None

    def __init__(self, parent, controller, simulator):
        tk.Frame.__init__(self,parent)

        self.simulator = simulator
        plt.ion()

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
    
        #Synapse selector
        self.synapse_label.grid(column=1,row=0, sticky='ne')
        self.browse_synapse_button.grid(column=2,row=0, sticky='ne')

        #Synapse mod selector.
        self.mod_label.grid(column=1,row=1, sticky='ne')
        self.browse_mod_button.grid(column=2,row=1, sticky='ne')

        #HOC selector.
        self.hoc_label.grid(column=1,row=2, sticky='ne')
        self.browse_hoc_button.grid(column=2,row=2, sticky='ne')

        #Mechanism selector.
        self.mech_label.grid(column=1,row=3, sticky='ne')
        self.browse_mech_button.grid(column=2,row=3, sticky='ne')        

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
        self.panel = ParameterPanel(self)
        self.panel.grid(column=3, row=0, rowspan= 100, columnspan = 4, sticky='nw')
        self.panel.update()

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

        #If all the synapse files have been selected. Generate the core then clean up to populate the synapse parameter list.
        if not (self.synapse_dir == '' or self.mod_dir == ''):
            self.simulator.synapse_json = self.synapse_dir
            self.simulator.synapse_mod = self.mod_dir
            
            #Generate the simulator's synpase parameter dict.
            self.simulator.generate_synapse_dict()

            #now populate the parameter panel synapse parameters.
            self.panel.generate_synapse_panel()

    def plot_graphs(self):
        #update simulator data.
        self.simulator.update_data()

        self.memvtime.clear()
        self.injvtime.clear()

        self.memline = self.memvtime.plot(self.simulator.time,self.simulator.membrane_potential)
        
        for key in self.simulator.currents:
            self.currentline.append(self.injvtime.plot(self.simulator.time,self.simulator.currents[key]))

        self.memcanvas.draw()
        self.injcanvas.draw()


class ParameterPanel(tk.Frame):

    parent_ui = None

    #GUI elements.
    run_button = None
    clamp_button = None

    tstop_feild = None
    vinit_feild = None
    clamp_field = None

    #Netstim feilds.
    stim_number_feild = None
    stim_interval_feild = None
    stim_start_feild = None

    #parameter feilds.
    parameter_feilds = []

    #Stores the parameters that can be changed in the synapse file.
    parameters = {}

    first_run = True

    def __init__(self,parent):
        tk.Frame.__init__(self,parent)

        self.parent_ui = parent

        #Create run button.
        self.run_button = tk.Button(self, text='Run', command=self.run_simulation)
        
        #Create current clamp button.
        

        #Create input fields for v_init and tstop.
        #tstop.
        tstop_label = tk.Label(self, text = 'tstop: ')
        self.tstop_feild = tk.Entry(self)
        self.tstop_feild.insert(0,str(self.parent_ui.simulator.tstop))
    
        #vinit.
        vinit_label = tk.Label(self, text = 'v_init: ')
        self.vinit_feild = tk.Entry(self)
        self.vinit_feild.insert(0,str(self.parent_ui.simulator.resting))

        #Netstim feilds.
        stim_number_label = tk.Label(self, text = 'Stim Count: ')
        self.stim_number_feild = tk.Entry(self)
        self.stim_number_feild.insert(0,str(self.parent_ui.simulator.stim_number))
        
        stim_interval_label = tk.Label(self, text = 'Stim Interval: ')
        self.stim_interval_feild = tk.Entry(self)
        self.stim_interval_feild.insert(0,str(self.parent_ui.simulator.stim_interval))
        
        stim_start_label = tk.Label(self, text = 'Stim Start: ')
        self.stim_start_feild = tk.Entry(self)
        self.stim_start_feild.insert(0,str(self.parent_ui.simulator.stim_start))

        #place everything.
        self.run_button.grid(column = 0, row = 0, sticky = 'n')
        
        tstop_label.grid(column = 1, row = 0, sticky = 'n')
        self.tstop_feild.grid(column = 2, row = 0, sticky = 'n')

        vinit_label.grid(column = 1, row = 1, sticky = 'n')
        self.vinit_feild.grid(column = 2, row = 1, sticky = 'n')

        stim_number_label.grid(column = 1, row = 2, sticky = 'n')
        self.stim_number_feild.grid(column = 2, row = 2, sticky = 'n')

        stim_interval_label.grid(column = 1, row = 3, sticky = 'n')
        self.stim_interval_feild.grid(column = 2, row = 3, sticky = 'n')

        stim_start_label.grid(column = 1, row = 4, sticky = 'n')
        self.stim_start_feild.grid(column = 2, row = 4, sticky = 'n')

    def generate_synapse_panel(self):
    #Go through the parameter dict and create a feild for each one.
        rowcount = 5
        for name in self.parent_ui.simulator.synapse_parameters:
            label = tk.Label(self, text= name + ': ')
            label.grid(column = 1, row = rowcount)

            entry = tk.Entry(self)
            entry.insert(0,str(self.parent_ui.simulator.synapse_parameters[name]))
            entry.grid(column = 2, row = rowcount)
            self.parameter_feilds.append(entry)

            rowcount += 1


    def run_simulation(self):

        #Check that each directory has been selected properly.
        if self.parent_ui.synapse_dir == '' or \
           self.parent_ui.hoc_dir == '' or     \
           self.parent_ui.mech_dir == '' or    \
           self.parent_ui.mod_dir == '':
            return


        #Chech if the simulator has already been initialized, if not initialize it
        #then run.

        #replace all the dashes with minus signes.
        self.parent_ui.simulator.resting = float(re.sub(u'\u2212','-',self.vinit_feild.get()))
        self.parent_ui.simulator.tstop = int(re.sub(u'\u2212','-',self.tstop_feild.get()))
        
        self.parent_ui.simulator.stim_number = int(self.stim_number_feild.get())
        self.parent_ui.simulator.stim_interval = int(self.stim_interval_feild.get())
        self.parent_ui.simulator.stim_start = int(self.stim_start_feild.get())


        #Cycle through the synapse entry feilds and set the values in the simulator.
        for feild,key in zip(self.parameter_feilds,self.parent_ui.simulator.synapse_parameters):
            self.parent_ui.simulator.synapse_parameters[key] = float(re.sub(u'\u2212','-',feild.get()))


        self.parent_ui.simulator.set_parameters(self.parent_ui.hoc_dir,
                                                self.parent_ui.mech_dir,
                                                self.parent_ui.synapse_dir,
                                                self.parent_ui.mod_dir)

        
        #if this is the first run, plot the graphs.
        if self.first_run == True:
            self.parent_ui.simulator.generate_core_init('template.tem')
            self.parent_ui.simulator.initialize_simulator()

            self.first_run = False

            
        #Now run the simulation.
        self.parent_ui.simulator.generate_core_simulator('template.tem')
        self.parent_ui.simulator.load_core()
        self.parent_ui.simulator.run_simulation()
        self.parent_ui.simulator.clean_up()

        self.parent_ui.plot_graphs()       

        

        

        

        



