from neuron import h
from sys import platform
import os
import json
import numpy as np

class Simulator:

    #Cell parameters.
    resting = -61.1 #mV
    tstop = 400 #ms

    #netstim parameters.
    stim_number = 12
    stim_interval = 12
    stim_start = 100

    membrane_potential = None
    time = None

    num_currents = 0
    
    '''
    Requires all 4 of these paremeters before the simulation is run.
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

    def generate_core_simulator(self, template_dir):
        
        core = 0
        synapseobject = ''
        mod_list = []

        current_names = []
        #Read through the synapse mod file and find the object name.
        with open(self.synapse_mod, 'r') as file: 
            
            for line in file:
                if 'POINT_PROCESS' in line:
                    synapseobject = line.split(' ')[1].replace('\n','')

                if 'NONSPECIFIC_CURRENT' in line:
                    keys = line.split(' ')

                    self.num_currents = len(keys) - 1
                    for key in keys[1:]:
                        current_names.append(key.replace(' ','').replace('\n','').replace(',','')) #probably the worst way of doing this
                
                if 'RANGE' in line:
                    parameters = line.split(' ')
                    parameters.pop(0)
                    
                    for par in parameters:
                        mod_list.append(par.replace('\n','').replace(',',''))
            file.close()

        cellobject = ''
        with open(self.cell_dir, 'r') as file:     
            for line in file:
                if 'begintemplate' in line:
                    cellobject = line.split(' ')[1].replace('\n','')
                    break
            file.close()

        mapping = [
            self.mech_dir         , self.cell_dir       , str(self.tstop)        ,
            str(self.resting)     , cellobject          , str(self.stim_interval),
            str(self.stim_number) , str(self.stim_start), synapseobject          ,
            str(self.num_currents)                                                ]

        synapse_parameters = {}
        with open(self.synapse_json, 'r') as file:
            synapse_parameters = json.load(file)
            file.close()

        with open(template_dir, 'r') as file:
            
            #Write the core hoc file.
            output = open('core.hoc', 'w')

            for line in file:
                if '@' in line:
                    #Loop through and set all the parameters. 
                    for key in synapse_parameters:
                        if key in mod_list:
                            output.write(line.replace('@',key).replace('%',synapse_parameters[key]))

                elif '*' in line:
                    #Regular parameters.
                    output.write(line.replace('*',mapping[core]))
                    core += 1
                
                elif '^' in line:
                    #Synapse recording objects
                    if '~' in line:
                        for i in range(self.num_currents):
                            output.write(line.replace('^',str(i)).replace('~',current_names[i]) + '\n')
                    else:
                        for i in range(self.num_currents):
                            output.write(line.replace('^',str(i)))
                
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
    
    def get_synapse_current(self, id):
        return list(h.input[id])

    def load_core(self):
        h.load_file('core.hoc')

    def run_simulation(self):
        h.run()
        
    def clean_up(self):
        os.remove('core.hoc')


        