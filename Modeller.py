import SynapseUI as UI
import Simulator as Sim 

def main():

    SynUI = UI.SynapseUI(className='Synapse UI',)
    SynUI.initialize(Sim.Simulator())
    SynUI.mainloop()
    
    


if __name__ == '__main__':
    main()
