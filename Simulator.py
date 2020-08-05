from neuron import h
from sys import platform
import os

class Simulator:

    def __init__(self,cell_dir, mech_dir, synapse_dir, synapse_mod):
        #Load in the files needed for synapse modelling.
        
        #On linux this path should be the x86_64 folder.
        #On windows this path should be nrnmechdll.
        if platform == "linux" or platform == "linux2" or platform == "darwin":
            h.nrn_load_dll(os.path.join(mech_dir, ".libs/libnrnmech.so")) # linux / OSX.
        else:
            h.nrnload_dll(mech_dir) # Windows.

        self.synapse_json = synapse_json
        self.synapse_mod = synapse_mod

        h.load_file(cell_dir)
        
        #Everything should be loaded in now.

    def generate_core_simulator(self, template_dir, core_prefix):
        
        core_dir = os.path.join(core_prefix,"core.hoc")

        with open(template_dir, 'r') as file:
            



        