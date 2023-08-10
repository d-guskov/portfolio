import random 
import ast
import math
import matplotlib.pyplot as plt 
import matplotlib.animation as animation 
import copy as c
import matplotlib.patches as mpa

# Initialization of the Node class; Node = Person

class Node:
    def __init__(self,key,coordinates,infection_date,neighbors):
        self.key=key
        self.coordinates=coordinates
        self.infection_date=infection_date
        self.neighbors=sorted(c.deepcopy(neighbors))
        self.active=True
        
        # State and color of the node, initially green representing 'healthy'
        
        self.color='green'
        

# Initialization of the Virus class; Data from an external file provided by Manuel Radons, a teaching assistent at the TU Berlin

class Virus:
    def __init__(self,time,incubation_period,contageous_period,transmissibility,graph):
        self.time=time
        self.incubation_period=incubation_period
        self.contageous_period=contageous_period
        self.transmissibility=transmissibility
        with open(graph,'r') as f:
            count = 0
            Nodes = [] 
            for line in f:
                split = line.split(";")
                Nodes.append(Node(count,ast.literal_eval(split[0]),-1,ast.literal_eval(split[1])))
                count = count + 1
                
        # Sorting in ascending order by keys
        
        self.graph = sorted(Nodes, key = lambda x: x.key)
        

    # A single step of virus spread
    
    def time_step(self):
        self.time+=1
        for Nd in self.graph:
            if Nd.active==True and Nd.infection_date!=-1:
                if self.time > (Nd.infection_date + self.incubation_period + self.contageous_period):
                    Nd.active=False
                    
                    # Node becomes inactive; corresponds to 'dead' or 'immune' state
                    
                    setattr(Nd, 'color','black')
                elif self.time > (Nd.infection_date + self.incubation_period):
                    for k in Nd.neighbors:
                        for Nd_k in self.graph:
                            if Nd_k.key==k:
                                if Nd_k.infection_date == -1:

                                    # Random infection
                                    
                                    if random.random() < self.transmissibility:
                                        Nd_k.infection_date=self.time

                                        # Node gets infected; corresponds to 'infected' state
                                        
                                        setattr(Nd_k, 'color','red')
                                        
                              
    # Simulate n steps of virus spread
    
    def time_steps(self, n):
        for i in range(n):
            self.time_step()


# Class for visualization

class VisualizeVirus(Virus):
    def __init__(self, V, days, inf_num):
        # Object of the Virus class
        self.V = V
        # Number of iterations or days, manual input
        self.days = days
        # Number of initially infected individuals, manual input
        self.inf_num = inf_num

    # Method to count healthy individuals on a given day
    
    def count_h(self):
        Virus = self.V
        c = 0
        for k in Virus.graph:
            if k.color == 'green':
                c += 1
        return c

    # Method to count infected individuals on a given day
    
    def count_i(self):
        Virus = self.V
        c = 0
        for k in Virus.graph:
            if k.color == 'red':
                c += 1
        return c

    # Method to count deceased/immunized individuals on a given day
    
    def count_d(self):
        Virus = self.V
        c = 0
        for k in Virus.graph:
            if k.color == 'black':
                c += 1
        return c
                

    # Method for visualizing the simulation
    
    def viz(self):
        Virus = self.V
        # Total number of days
        n = self.days + 1
        # Number of healthy, infected, deceased/immunized individuals at the beginning
        h = self.count_h()  
        i = self.count_i()  
        d = self.count_d()
        # Desired number of initial infections
        f = self.inf_num
        # Randomly select nodes to start infections and initiate virus spread
        K = random.sample(Virus.graph, f)  
        for k in K:
            setattr(k, 'infection_date', 0)
            # Set initial infections to red color
            setattr(k, 'color', 'red')
        # Create the figure and set the title
        fig, ax = plt.subplots(figsize=(6, 5))  
        ax.set_title('Programming Project: Simulation of Virus Spread, day = 0')  
        
        # Legend settings
        
        green_patch = mpa.Patch(color='green', label='Healthy ({0})'.format(h))
        red_patch = mpa.Patch(color='red', label='Infected ({0})'.format(i))
        black_patch = mpa.Patch(color='black', label='Dead ({0})'.format(d))
        plt.legend(handles=[green_patch, red_patch, black_patch], bbox_to_anchor=(0.77, -0.06),
                   fontsize='small', ncol=3)  

        # Scatter plot of nodes with their colors and coordinates
        
        scat = ax.scatter([Nd.coordinates[0] for Nd in Virus.graph], [Nd.coordinates[1] for Nd in Virus.graph],
                          c=[Nd.color for Nd in Virus.graph], s=30)

        # Function to update the animation at each step
        
        def update(i, Virus):
            Virus.time_step()  
            h = self.count_h()  
            l = self.count_i()  
            d = self.count_d()
            # Get updated colors
            c = [Nd.color for Nd in Virus.graph]
            # Update node colors
            scat.set_color(c)
            # Update title
            ax.set_title('Programming Project: Simulation of Virus Spread, Day = {0}'.format(i))
            
            
            # Update legend with new counts
            
            green_patch = mpa.Patch(color='green', label='Healthy ({0})'.format(h))
            red_patch = mpa.Patch(color='red', label='Infected ({0})'.format(l))
            black_patch = mpa.Patch(color='black', label='Dead ({0})'.format(d))
            
            # Update legend with new information
            
            plt.legend(handles=[green_patch, red_patch, black_patch], bbox_to_anchor=(0.77, -0.06),
                       fontsize='small', ncol=3)
            
            # Return the updated scatter plot
            return scat,  

        # Create and display the animation
        
        anim = animation.FuncAnimation(fig, update, frames=[i for i in range(n)], fargs=(Virus,),
                                      interval=500, repeat=False)
        plt.show()  

    
# Starting the simulation automatically, other options graph_dist_3.in and graph_dist_4.in

if __name__ == "__main__":
    V = Virus(0, 4, 10, 0.5, "graph_dist_2.in")
    S = VisualizeVirus(V, 100, 3)
    S.viz()
