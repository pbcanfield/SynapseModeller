from neuron import h
from sys import platform
import os
import json

class Simulator:

    def __init__(self,cell_dir, mech_dir, synapse_dir, synapse_mod, resting=-70):
        #Load in the files needed for synapse modelling.
        
        #On linux this path should be the x86_64 folder.
        #On windows this path should be nrnmechdll.
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            self.mech_dir = os.path.join(mech_dir, ".libs/libnrnmech.so")
        else:
            self.mech_dir = mech_dir

        self.synapse_json = synapse_dir
        self.synapse_mod = synapse_mod
        self.resting = resting
        self.cell_dir = cell_dir
        
        #Everything should be loaded in now.

    def generate_core_simulator(self, template_dir):
        
        core = 0
        synapseobject = ''
        mod_list = []
        #Read through the synapse mod file and find the object name.
        with open(self.synapse_mod, 'r') as file: 
            
            for line in file:
                if 'POINT_PROCESS' in line:
                    synapseobject = line.split(' ')[1].replace('\n','')
                
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

        mapping = {
            0:self.mech_dir,
            1:self.cell_dir,
            2:str(self.resting),
            3:cellobject,
            4:synapseobject,
        }

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
                else:
                    output.write(line)

            output.close()
            file.close()
        
    def load_core(self):
        h.load_file('core.hoc')

    def run_simulation(self):
        h.run()
        
    def clean_up(self):
        os.remove('core.hoc')


        