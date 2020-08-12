import SynapseUI as UI
import Simulator as sim 

def main():

    simulator = sim.Simulator('./cell/BC.hoc','./cell/x86_64', 'synapse.json', './cell/modfiles/pyr2pyr.mod')

    simulator.generate_core_simulator('template.tem')
    simulator.load_core()
    simulator.run_simulation()
    simulator.clean_up()


    '''
    SynUI = UI.SynapseUI(className='Synapse UI')
    SynUI.mainloop()
    '''


if __name__ == '__main__':
    main()
