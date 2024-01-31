from my_pgsql import mydb 
import random
import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd 
import pygad
# class for doing stuff on postgresql in a loop

def plot_df(df,xcols,ycols,markers):
    fig,ax=plt.subplots(2,1)

    for no,col in enumerate(ycols):
        if xcols is None:
            df['index']=df.index
            xcol='index'
        else:
            xcol=xcols[no]
        ycol=ycols[no]
        ax[0].plot(df[xcol],df[ycol],label=col,marker=markers[no])

    plt.show()



def plot_peaks_and_vallies(prices,peaks,vallies,wall_points):
    print(peaks)
    print(vallies)


    fig,ax=plt.subplots(2,1)
    ax[0].plot(prices)
    ax[0].plot(peaks,  [prices[i] for i in peaks],'rv')
    ax[0].plot(vallies, [prices[i] for i in vallies],'g^')


    # print wall points as vertical lines 
    for wp in wall_points:
        ax[0].axvline(wp[0],color='r')
        ax[0].axvline(wp[1],color='r')

    plt.show()
    
    
#df=mydb().execute_select('select * from signals')
## save df to csv 
#df.to_csv('raw_data.csv',index=False)
df=pd.read_csv('raw_data.csv')



# sum all green candles 
df['green_candles']=df.apply(lambda x: 1 if x['close']>x['open'] else 0,axis=1)
max_roi=df['green_candles'].sum()


prices=df['close'].tolist()
min_index,max_index=0,len(prices)-1
n=10
# pick n peaks and n valleys randomly 

def choose_peaks_and_vallies(prices,n):
    n=10
    peaks=[random.randint(min_index,max_index) for i in range(n)]
    vallies=[random.randint(min_index,max_index) for i in range(n)]
    return peaks,vallies

# function for calculating roi on peaks and vallies
def calculate_roi(prices,peaks,vallies):
    roi=0
    for i in range(len(peaks)):
        roi+=prices[peaks[i]]-prices[vallies[i]]
    return roi

# plot price and peaks and vallies with subplots 

# Define the fitness function
import numpy as np

# Define the fitness function

def on_generation(ga_instance):
    pass
    #print("Generation : ", ga_instance.generations_completed)
    #print("Best fitness so far : ", ga_instance.best_solution()[1])

class FitnessFunction:
    def __init__(self, wall_points):
        self.wall_points = wall_points
        self.pop_wps=[]

    def fitness_func(self, ga_instance, solution, solution_idx):


        
        valleys = [int(solution[i]) for i in range(len(solution)) if i % 2 != 0]
        peaks = [int(solution[i]) for i in range(len(solution)) if i % 2 == 0]
        wps_to_pop=[]
        roi = 0
        for v, p in zip(valleys, peaks):
            roi += prices[p] - prices[v]
            
            for no,wp in enumerate(self.wall_points):

                
                check_conditions=[]

                
                condition1 = v<=wp[0] and p <=wp[0]
                condition2 = v>=wp[1] and p >=wp[1]
                condition3 = wp[0]<=v and p <= wp[1]
                condition4= v<p
                condition5= [int(v),int(p)] not in self.wall_points
                #print(condition5)
                
                check_condition = (condition1 | condition2 | condition3  ) & condition4 & condition5 
                check_conditions.append(check_condition)
                
                if condition3 and check_condition:
                    self.pop_wps.append(no)
                # if condition 3 is met then pop this
           
            if all(check_conditions) :
                                        
                return roi 
            
            if not all(check_conditions) :
                #print(self.wall_points,v,p,check_condition,[condition1,condition2,condition3,condition4])
                return 0





NG=100000
# Define the genetic algorithm
# Create an instance of the FitnessFunction class with the desired wall_points

fitness_function_instance = FitnessFunction([[0,len(prices)-1] ])

# Use the fitness_func method of the fitness_function_instance as the fitness function for PyGAD


# Run the genetic algorithm
N=0
VS=[]
PS=[]
while N<10:
    N+=1
    ga_instance = pygad.GA(
        num_generations=100,
        num_parents_mating=5,
        fitness_func=fitness_function_instance.fitness_func,
        sol_per_pop=50,
        num_genes=2,
        init_range_low=0,
        init_range_high=len(prices)-1,
        mutation_percent_genes=0.1,
        on_generation=on_generation
    )
    ga_instance.run()
    # Get the solution of the genetic algorithm
    solution, solution_fitness, solution_idx = ga_instance.best_solution()
    valleys = solution[:len(solution)//2].astype(int)
    peaks = solution[len(solution)//2:].astype(int)
    VS.append(valleys[0])
    PS.append(peaks[0])
    

    
    fitness_function_instance.wall_points += [[int(valleys), int(peaks)]]    
    print(fitness_function_instance.wall_points)
    

print(PS)
print(VS)
plot_peaks_and_vallies(prices=prices,peaks=PS,vallies=VS,wall_points=fitness_function_instance.wall_points)

print("Best solution : ", solution)
print("Solution fitness : ", solution_fitness)




# Print the peaks and valleys
print("Peaks : ", peaks)
print("Valleys : ", valleys)

print("Best solution : ", solution)
print("Solution fitness : ", solution_fitness)


