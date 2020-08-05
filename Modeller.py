import SynapseUI as UI
import Simulator as sim 

def main():

    simulator = sim.Simulator("./cell/BC.hoc","./cell/x86_64", "synapse.json")

    '''
    SynUI = UI.SynapseUI(className='Synapse UI')
    SynUI.mainloop()
    '''


if __name__ == '__main__':
    main()
