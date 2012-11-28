__author__ = 'Palli'
from random import randrange
import sys
import time
import math

def doGen( size=10000 ):
    return list("some unique object %d" % ( i, ) for i in xrange(size))

def print_timing (func):
    def wrapper (*arg):
        t1 = time.time ()
        res = func (*arg)
        t2 = time.time ()
        print ("{} took {} ms".format (func.__name__, (t2 - t1) * 1000.0))
        return res

    return wrapper

class GAP:
    def __init__(self, filename, Np, Nc, generations):

        self.Np = Np
        self.Nc = Nc
        self.generations = generations

        self.number_of_agents = 0
        self.number_of_tasks = 0
        self.evaluations_to_best = 0
        self.evaluations = 0
        self.agents_max_capacity = []
        self.resource_matrix = []
        self.cost_matrix = []
        self.best_fitness = sys.maxint
        self.best_solution = None

        # open data file
        file = open(filename, 'r')

        # parse file into lines and remove empty lines
        lines = file.read().split('\n')
        lines = [line for line in lines if line != ""]

        line = lines[1].split()
        self.number_of_agents = int(line[0])
        self.number_of_tasks = int(line[1])

        # capacity constraint for each agent
        agents_capacity = lines[2].split(" ")
        agents_capacity = [capacity for capacity in agents_capacity if capacity != ""]
        for capacity in agents_capacity:
            self.agents_max_capacity.append(int(capacity))

        # work units required
        for i in range(self.number_of_agents):
            tasks = lines[3+i].split(" ")
            tasks = [task for task in tasks if task != ""]
            temp = []
            for j in range(self.number_of_tasks):
                temp.append(int(tasks[j]))
            self.resource_matrix.append(temp)

        # cost incurred for agent i on task j
        for i in range(self.number_of_agents):
            costs = lines[3+i+self.number_of_agents].split(" ")
            costs = [cost for cost in costs if cost != ""]
            temp = []
            for j in range(self.number_of_tasks):
                temp.append(int(costs[j]))
            self.cost_matrix.append(temp)

    def __random_solution(self):
        solution = []
        for task_nr in range(self.number_of_tasks):
            random_agent = randrange(self.number_of_agents)
            solution.append(random_agent)
        return solution

    def __random_solution_constraints(self):
        solution = []
        agents_capacity = self.agents_max_capacity[:]
        for task_nr in range(self.number_of_tasks):
            tries = 0
            while tries < 500:
                random_agent = randrange(self.number_of_agents)
                resource = self.resource_matrix[random_agent][task_nr]
                if resource <= agents_capacity[random_agent]:
                    solution.append(random_agent)
                    agents_capacity[random_agent] -= resource
                    break
                else:
                    tries += 1
            else:
                return None
        return solution

    def random_solutions(self):
        solutions = []
        for m in range(self.Np):
            solution = None

            for i in range(1000):
                solution = self.__random_solution()
                if self.feasible(solution):
                    self.random_lookups = i
                    break
                else:
                    solution = None

            if not solution:
                for j in range(1000):
                    solution = self.__random_solution_constraints()
                    if self.feasible(solution):
                        self.random_lookups = i+j
                        break

            solutions.append(solution)
        return solutions

    def fitness(self, solution):
        fitness = 0
        if not self.feasible(solution):
            fitness = sys.maxint
        else:
            for task_nr in range(self.number_of_tasks):
                agent_nr = solution[task_nr]
                fitness += self.cost_matrix[agent_nr][task_nr]

        return fitness

    def feasible(self, solution):
        if not solution:
            return False

        agents_capacity = self.agents_max_capacity[:]

        for task_nr in range(self.number_of_tasks):
            agent = solution[task_nr]
            resources = self.resource_matrix[agent][task_nr]
            if resources > agents_capacity[agent]:
                return False
            else:
                agents_capacity[agent] -= resources

        return True


    def tournament_selection(self, k, pop):
        selections = []
        for i in range(k):
            selections.append(pop[randrange(self.Np)])

        # randomly selects fittest at start to counter always selecting
        # at fixed location if all have max fitness.
        fittest = selections[randrange(k)]
        fittest_fitness = self.fitness(fittest)

        # find fittest in group of selected
        for selection in selections:
            fitness = self.fitness(selection)
            if fittest_fitness > fitness:
                fittest = selection
                fittest_fitness = fitness

        return fittest

    def uniform_crossover(self, p1, p2):
        child = []
        for i in range(len(p1)):
            if randrange(2) == 0:
                child.append(p1[i])
            else:
                child.append(p2[i])

        return child

    def evaluate(self, solution):
        self.evaluations += 1
        fitness = self.fitness(solution)
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_solution = solution
            self.evaluations_to_best = self.evaluations

    def mutate(self, solution):
        for i in range(self.number_of_tasks/8):
            rand_loc = randrange(self.number_of_tasks)
            rand_value = randrange(self.number_of_agents)

            solution[rand_loc] = rand_value
        return solution

    def replace(self, pop, cpop):
        for c in cpop:
            pop[random.randrange(self.Np)] = c

        return pop

    def run(self):
        self.pop = self.random_solutions()

        for i in range(self.generations):
            cpop = []
            while len(cpop) < self.Nc:
                p1 = self.tournament_selection(2, self.pop)
                p2 = self.tournament_selection(2, self.pop)

                c1 = self.uniform_crossover(p1,p2)
                c2 = self.uniform_crossover(p1,p1)

                self.evaluate(c1)
                self.evaluate(c2)

                c1 = self.mutate(c1)
                c2 = self.mutate(c2)

                cpop.append(c1)
                cpop.append(c2)

            self.pop =  cpop

        return self.best_fitness

@print_timing
def run_30_times(filename):
    gap = GAP(filename, 100, 100, 100)
    total = 0.0
    for i in range(30):
        total += gap.run()
    print "mean of 30 runs"
    print "mean best fitness %f" %(total / 30.0)
    print "genotype %s" %gap.best_solution
    print "best fitness: %i" %gap.best_fitness
    print "feasable: %s" %gap.feasible(gap.best_solution)
    print "evaluations to best %i" %gap.evaluations_to_best


    #solution = [0,0,2,1,0,2,0,0,1,1,0,2,2,2,1]
    #print gap.fitness(solution)

@print_timing
def run_10_times(filename):
    gap = GAP(filename, 100, 100, 100)
    total = 0.0
    for i in range(10):
        total += gap.run()
    print total / 10.0



#run_30_times('data/D3-15.dat')         # finding rand 46 iteration  , with repair 48
#run_30_times('data/D20-100.dat')       # finding rand 495 iteration , with repair 336
#run_30_times('data/C10-100.dat')       # finding rand never         , with repair 999
run_30_times('data/C30-500.dat')       # finding rand never         , with repair 999
#run_30_times('data/E10-100.dat')       # finding rand 50 iteration  , with repair 67
#run_30_times('data/E50-1000.dat')      # finding rand never        , with repair 999


"""
mean of 30 runs
mean best fitness 768.566667
genotype [1, 0, 2, 0, 2, 2, 0, 0, 1, 0, 1, 1, 0, 2, 1]
best fitness: 766
feasable: True
evaluations to best 353840
run_30_times took 83687.9999638 ms

mean of 30 runs
mean best fitness 5585.900000
genotype [12, 12, 2, 14, 8, 18, 10, 0, 14, 4, 16, 0, 3, 5, 1, 14, 18, 13, 13, 16, 4, 16, 4, 3, 15, 11, 15, 16, 16, 6, 0, 3, 1, 8, 8, 1, 6, 15, 15, 19, 6, 18, 14, 13, 9, 16, 4, 1, 6, 11, 10, 9, 9, 17, 5, 10, 8, 1, 10, 2, 0, 17, 6, 7, 15, 5, 7, 4, 5, 0, 17, 16, 11, 3, 14, 14, 1, 13, 3, 15, 19, 10, 17, 19, 5, 2, 8, 10, 5, 2, 14, 16, 2, 13, 6, 4, 9, 9, 6, 15]
best fitness: 5546
feasable: False
evaluations to best 2133256
run_30_times took 487625.0 ms

mean of 30 runs
mean best fitness 2573.000000
genotype [1, 4, 3, 4, 1, 4, 6, 9, 6, 6, 2, 0, 2, 0, 5, 9, 0, 8, 2, 2, 9, 9, 5, 0, 0, 1, 8, 8, 3, 4, 1, 8, 1, 0, 2, 4, 8, 4, 6, 3, 1, 9, 1, 4, 2, 3, 0, 3, 2, 9, 5, 8, 2, 6, 7, 9, 6, 7, 7, 0, 7, 0, 8, 4, 9, 0, 0, 7, 4, 7, 6, 1, 9, 8, 5, 5, 8, 3, 4, 1, 8, 8, 3, 9, 5, 6, 2, 0, 3, 6, 6, 5, 5, 3, 6, 7, 5, 5, 8, 5]
best fitness: 2573
feasable: False
evaluations to best 78
run_30_times took 238495.000124 ms

mean of 30 runs
mean best fitness 13940.933333
genotype [27, 9, 23, 26, 27, 9, 19, 2, 24, 18, 18, 4, 8, 10, 15, 13, 3, 25, 19, 26, 10, 9, 7, 8, 0, 4, 18, 27, 25, 12, 22, 0, 23, 14, 23, 10, 27, 27, 26, 18, 18, 15, 13, 8, 25, 15, 4, 9, 3, 8, 27, 17, 24, 23, 12, 21, 26, 29, 29, 16, 2, 22, 3, 6, 24, 21, 2, 29, 3, 7, 20, 1, 7, 29, 5, 5, 3, 0, 28, 8, 1, 28, 2, 6, 7, 7, 7, 7, 5, 0, 19, 3, 1, 11, 26, 14, 3, 11, 12, 21, 13, 2, 13, 25, 5, 25, 22, 29, 8, 1, 17, 21, 18, 27, 11, 21, 11, 21, 13, 21, 11, 17, 19, 1, 28, 0, 18, 8, 29, 17, 9, 0, 18, 15, 21, 14, 15, 4, 18, 17, 12, 3, 2, 15, 16, 23, 0, 3, 22, 22, 6, 27, 13, 22, 16, 24, 14, 6, 7, 13, 26, 17, 29, 17, 26, 21, 17, 19, 11, 13, 13, 7, 13, 27, 4, 13, 11, 27, 0, 15, 14, 20, 15, 28, 19, 0, 17, 26, 28, 26, 16, 2, 9, 5, 2, 19, 28, 28, 7, 26, 14, 2, 28, 17, 16, 19, 20, 14, 9, 28, 13, 1, 17, 6, 23, 0, 5, 1, 9, 27, 18, 21, 17, 17, 29, 12, 14, 25, 23, 23, 18, 17, 26, 17, 24, 26, 7, 5, 14, 1, 17, 6, 29, 7, 21, 7, 0, 19, 9, 26, 21, 8, 29, 25, 1, 2, 11, 1, 22, 20, 28, 9, 9, 27, 22, 25, 16, 3, 10, 26, 4, 24, 5, 24, 16, 14, 9, 22, 6, 21, 0, 24, 25, 7, 5, 29, 3, 20, 12, 19, 16, 4, 24, 24, 20, 19, 22, 15, 6, 4, 25, 23, 25, 21, 14, 21, 24, 28, 10, 18, 23, 4, 14, 25, 16, 25, 26, 16, 2, 25, 28, 9, 26, 20, 9, 19, 24, 21, 11, 22, 4, 2, 13, 11, 29, 11, 16, 23, 29, 11, 13, 28, 2, 20, 11, 28, 9, 29, 7, 8, 9, 19, 7, 23, 8, 29, 19, 15, 19, 27, 10, 23, 27, 14, 20, 0, 8, 16, 3, 25, 1, 7, 4, 10, 25, 28, 3, 16, 25, 22, 6, 16, 14, 4, 23, 6, 27, 19, 7, 27, 24, 27, 22, 8, 27, 24, 16, 8, 24, 12, 2, 16, 15, 12, 28, 10, 12, 28, 25, 15, 12, 1, 25, 12, 0, 16, 23, 1, 4, 3, 23, 3, 12, 14, 28, 5, 2, 4, 2, 24, 18, 1, 15, 1, 4, 2, 7, 28, 8, 1, 8, 10, 24, 20, 21, 11, 5, 12, 14, 8, 0, 20, 5, 8, 26, 12, 29, 1, 24, 15, 12, 11, 16, 6, 24, 26, 20, 15, 10, 6, 6, 16, 1, 14, 12, 20, 1, 9, 6, 6, 20, 14, 10, 17, 6, 6, 10, 0, 20, 11, 8, 7, 11, 26, 4, 24, 24, 25, 16, 6]
best fitness: 13803
feasable: False
evaluations to best 230086
run_30_times took 1153394.00005 ms
"""



