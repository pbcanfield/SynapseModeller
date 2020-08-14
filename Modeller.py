import SynapseUI as UI
import Simulator as sim 

def main():

    

    '''
    simulator = sim.Simulator()

    simulator.set_parameters('./cell/BC.hoc','./cell', 'synapse.json', './cell/modfiles/pyr2pyr.mod')
    simulator.generate_core_simulator('template.tem')
    simulator.load_core()
    simulator.run_simulation()
    simulator.clean_up()
    '''

  
    simulator = sim.Simulator()

    SynUI = UI.SynapseUI(className='Synapse UI')
    SynUI.set_simulator(simulator)
    
    SynUI.mainloop()
    
    


if __name__ == '__main__':
    main()
