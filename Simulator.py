from neuron import h
from sys import platform
import os
import json
import numpy as np
from importlib import reload


class Simulator:

    #Cell parameters.
    resting = -61.1 #mV
    tstop = 400 #ms

    #netstim parameters.
    stim_number = 12
    stim_interval = 12
    stim_start = 100

    membrane_potential = []
    time = []

    num_currents = 0
    currents = {}
    
    synapse_parameters = {}

    synapse_json = ''
    synapse_mod = ''
    cell_dir = ''
    mech_dir = ''

    core_suffix = 0

    '''
    Requires all 4 of these paremeters before generate_core_simulator is run.
    1)  The path to the cell template
    2)  The path to the either the mechanism dll (windows) or the x86_64 folder (linux)
    3)  The path to the synapse json file
    4)  The path to the synapse mod file
    '''
    def set_parameters(self, cell_dir, mech_dir, synapse_dir, synapse_mod):
        #Load in the files needed for synapse modelling.
        
        #On linux this path should be the x86_64 folder.
        #On windows this path should be nrnmechdll.
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.mech_dir = os.path.join(mech_dir, ".libs/libnrnmech.so")
        else:
            self.mech_dir = mech_dir

        self.synapse_json = synapse_dir
        self.synapse_mod = synapse_mod
        self.cell_dir = cell_dir

    #Requires that the synapse mod directory and the synapse json directory have
    #already been set.
    def generate_synapse_dict(self):
        mod_list = []
        #Read through the synapse mod file and find the object name.
        with open(self.synapse_mod, 'r') as file: 
            
            for line in file:      
                if 'RANGE' in line:
                    parameters = line.split(' ')
                    parameters.pop(0)
                    
                    for par in parameters:
                        mod_list.append(par.replace('\n','').replace(',',''))
            file.close()

        synapse_params = {}
        with open(self.synapse_json, 'r') as file:
            synapse_params = json.load(file)
            file.close()

        self.synapse_parameters.clear()
        #Loop through and set all the parameters. 
        for key in synapse_params:
            if key in mod_list:
                self.synapse_parameters[key] = synapse_params[key]

    def generate_core_init(self, template_dir):
        
        with open(self.synapse_mod, 'r') as file:
            for line in file:
                if 'NONSPECIFIC_CURRENT' in line:
                    keys = line.split(' ')
                    self.num_currents = len(keys) - 1    
                    for key in keys[1:]:
                        self.currents[key.replace(' ','').replace('\n','').replace(',','')] = [] #probably the worst way of doing this
            file.close()

        synapseobject = ''
        #Read through the synapse mod file and find the object name.
        with open(self.synapse_mod, 'r') as file: 
            
            for line in file:
                if 'POINT_PROCESS' in line:
                    synapseobject = line.split(' ')[1].replace('\n','')

                
            file.close()

        cellobject = ''
        with open(self.cell_dir, 'r') as file:     
            for line in file:
                if 'begintemplate' in line:
                    cellobject = line.split(' ')[1].replace('\n','')
                    break
            file.close()

        mapping = [
            self.mech_dir          ,
            self.cell_dir          ,
            str(self.num_currents) ,
            cellobject             ,
            synapseobject 

        ]

        with open(template_dir, 'r') as file:
            core = 0
            output = open('init.hoc', 'w')

            for line in file:
                if '#' in line:
                    line = line.replace('#','')
                    if '*' in line:
                        output.write(line.replace('*',mapping[core]))
                        core += 1
                    elif '^' in line:
                        #Synapse recording objects
                        if '~' in line:
                            for i,key in zip(range(self.num_currents),self.currents):
                                output.write(line.replace('^',str(i)).replace('~',key))
                        else:
                            for i in range(self.num_currents):
                                output.write(line.replace('^',str(i)))

                    else:
                        output.write(line)

            
            output.close()
            file.close()
        
    #Requires that all 4 directories have already been set and
    #that generate_synapse_dict() has already been called.
    def generate_core_simulator(self, template_dir):
        core = 0
        

        mapping = [
            str(self.core_suffix)  ,  
            str(self.tstop)        ,
            str(self.resting)      ,
            str(self.stim_interval),
            str(self.stim_number)  ,
            str(self.stim_start)   ,
        ]

        with open(template_dir, 'r') as file:
            
            #Write the core hoc file.
            output = open('core'+ str(self.core_suffix) +'.hoc' , 'w')

            for line in file:
                
                if '#' in line:
                    continue
                elif '@' in line:
                    #Loop through and set all the parameters. 
                    for key in self.synapse_parameters:
                        output.write(line.replace('@',key).replace('%',str(self.synapse_parameters[key])))

                elif '*' in line:
                    #Regular parameters.
                    output.write(line.replace('*',mapping[core]))
                    core += 1
                
                
                else:
                    output.write(line)

            output.close()
            file.close()
            
    def get_membrane(self):
        return list(h.membrane)

    def get_input(self):
        return list(h.input)

    def get_time(self):
        return list(h.time)
    
    def update_data(self): 
        self.time = self.get_time()
        self.membrane_potential = self.get_membrane()

        for i,key in zip(range(self.num_currents),self.currents):
            self.currents[key] = self.get_synapse_current(i)
    
    def get_synapse_current(self, id):
        return list(h.input[id])

    def initialize_simulator(self):
        h.load_file('init.hoc')
        #os.remove('init.hoc')

    def load_core(self):
        h.load_file('core'+ str(self.core_suffix) +'.hoc')
        
    def run_simulation(self):
        h.finitialize(self.resting)
        h('run' + str(self.core_suffix) + '()')
        self.core_suffix += 1
        
    def clean_up(self):
        #Delete the previous core file.
        os.remove('core'+ str(self.core_suffix - 1) +'.hoc')



        