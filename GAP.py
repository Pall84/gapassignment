__author__ = 'Palli'
import random
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

    def random_solution(self):
        solutions = []
        for m in range(self.Np):
            tries = 0
            solution = None
            while tries < 1000:
                solution = []
                for n in range(self.number_of_tasks):
                    solution.append(random.randrange(self.number_of_agents))
                    tries += 1
                if not self.over_worked(solution):
                    break
            solutions.append(solution)
        return solutions

    def repair(self, solution):
        agents_capacity =[]
        for i in range(self.number_of_agents):
            agents_capacity.append(0)
        for task_nr in range(self.number_of_tasks):
            agent_nr = solution[task_nr]
            agents_capacity[agent_nr] += self.resource_matrix[agent_nr][task_nr]

        for j in range(self.number_of_agents):
            if agents_capacity[j] > self.agents_max_capacity[j]:
                return True

    def fitness(self, solution):
        fitness = 0
        if self.over_worked(solution):
            fitness = sys.maxint
        else:
            for task_nr in range(self.number_of_tasks):
                agent_nr = solution[task_nr]
                fitness += self.cost_matrix[agent_nr][task_nr]

        return fitness

    def over_worked(self, solution):
        agents_capacity =[]
        for i in range(self.number_of_agents):
            agents_capacity.append(0)
        for task_nr in range(self.number_of_tasks):
            agent_nr = solution[task_nr]
            agents_capacity[agent_nr] += self.resource_matrix[agent_nr][task_nr]

        for j in range(self.number_of_agents):
            if agents_capacity[j] > self.agents_max_capacity[j]:
                return True

        return False

    def tournament_selection(self, k, pop):
        selections = []
        for i in range(k):
            selections.append(pop[random.randrange(self.Np)])

        # randomly selects fittest at start to counter always selecting
        # at fixed location if all have max fitness.
        fittest = selections[random.randrange(k)]
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
            if random.randrange(2) == 0:
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
        rand_loc = random.randrange(self.number_of_tasks)
        rand_value = random.randrange(self.number_of_agents)

        solution[rand_loc] = rand_value
        return solution

    def replace(self, pop, cpop):
        for c in cpop:
            pop[random.randrange(self.Np)] = c

        return pop

    def run(self):
        self.pop = self.random_solution()

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
    best_fitness = sys.maxint
    genotype = ""
    evaluation = 0
    gap = GAP(filename, 100, 100, 100)
    total = 0.0
    for i in range(30):
        fitness = gap.run()
        total += fitness
        if fitness < best_fitness:
            best_fitness = fitness
            genotype = gap.best_solution
            evaluation = gap.evaluations_to_best
    print "mean fitness of 30 runs"
    print total / 30.0
    print
    print "best solution"
    print "genotype: " + str(genotype)
    print "fitness: " + str(best_fitness)
    print "evaluations to best: " + str(evaluation)


    #solution = [0,0,2,1,0,2,0,0,1,1,0,2,2,2,1]
    #print gap.fitness(solution)

@print_timing
def run_10_times(filename):
    gap = GAP(filename)
    total = 0.0
    for i in range(10):
        total += gap.run()
    print total / 10.0



#run_10_times('data/D3-15.dat')

run_30_times('data/D3-15.dat')





