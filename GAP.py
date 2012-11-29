__author__ = 'Palli'
from random import randrange
import sys
import time
from copy import copy
import thread

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
    def __init__(self, filename, Np, generations):

        self.Np = Np
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

    def random_solutions(self, N):
        solutions = []
        for m in range(N):
            solution = None

            for j in range(1000):
                solution = self.__random_solution_constraints()
                if self.feasible(solution):
                    self.random_lookups = j
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
            self.best_solution = copy(solution)
            self.evaluations_to_best = self.evaluations

    def mutate(self, solution):
        for i in range(self.number_of_tasks/5):
            rand_loc = randrange(self.number_of_tasks)
            rand_value = randrange(self.number_of_agents)

            solution[rand_loc] = rand_value
        return solution

    def replace(self, N, P, C):
        """ replaces pop with best N from C or P
        """
        new_pop = []
        for i in range(N):
            best_member_p = self.__best_member(P)
            best_member_c = self.__best_member(C)
            if self.fitness(best_member_p) < self.fitness(best_member_c):
                new_pop.append(best_member_p)
            else:
                new_pop.append(best_member_c)
        return new_pop

    def __best_member(self, pop):
        """ find best member in population. """
        best_member = None
        best_fitness = sys.maxint

        # check every member in population.
        for member in pop:
            fitness = self.fitness(member)
            if fitness < best_fitness:
                best_member = member
                best_fitness = fitness

        # return reference to best member.
        return best_member

    def parent_selection(self, pop):
        random_parent = randrange(len(pop))
        parent = pop[random_parent]
        pop.remove(parent)
        return parent

    def distance(self, p1, p2):
        distance = self.number_of_tasks
        for gene in range(self.number_of_tasks):
            if p1[gene] == p2[gene]:
                distance -= 1
        return distance

    def hux(self, p1, p2):
        child = []
        p1_is_next = True
        for gene in range(self.number_of_tasks):
            p1_gene = p1[gene]
            p2_gene = p2[gene]
            if p1_gene == p1_gene:
                child.append(p1_gene)
            else:
                if p1_is_next:
                    child.append(p1_gene)
                    p1_is_next = False
                else:
                    child.append(p2_gene)
                    p1_is_next = True

        return child

    def diverge(self, P):
        best_member = self.__best_member(P)

        new_pop = []
        pop_size = len(P)
        for index in range(pop_size):
            new_member = copy(best_member)
            for run in range(self.number_of_tasks/3):
                random_flip = randrange(self.number_of_agents)
                random_gene = randrange(self.number_of_tasks)
                new_member[random_gene] = random_flip
            new_pop.append(new_member)
        pop = new_pop

    def run_ga(self):
        Np = self.Np
        Nc = self.Nc
        P = self.random_solutions(Np)

        for i in range(self.generations):
            C = []
            while len(C) < Nc:
                p1 = self.tournament_selection(2, P)
                p2 = self.tournament_selection(2, P)

                c1 = self.uniform_crossover(p1,p2)
                c2 = self.uniform_crossover(p1,p1)

                self.evaluate(c1)
                self.evaluate(c2)

                c1 = self.mutate(c1)
                c2 = self.mutate(c2)

                C.append(c1)
                C.append(c2)

            P =  C

        return self.best_fitness

    def run_chc(self):
        L = self.number_of_tasks
        N = self.Np
        P = self.random_solutions(N)
        Thresh = L/4
        for j in  range(self.generations):
            C = []
            parent_pool = copy(P)
            for i in range(N/2):
                p1 = self.parent_selection(parent_pool)
                p2 = self.parent_selection(parent_pool)
                self.evaluate(p1)
                self.evaluate(p2)
                if self.distance(p1, p2) >= Thresh:
                    c1 = self.hux(p1,p2)
                    c2 = self.hux(p1,p2)
                    self.evaluate(c1)
                    self.evaluate(c2)
                    C.append(c1)
                    C.append(c2)
            if len(C) <= 0:
                L = L - 1
                if L <= 0:
                    self.diverge(P)
                    L = self.number_of_tasks
            else:
                P = self.replace(N, P, C)
        return self.best_fitness

@print_timing
def run_30_times_chc(filename,n,g):
    gap = GAP(filename, n, g)
    total = 0.0
    for i in range(30):
        total += gap.run_chc()
        if i == 10:
            print "%s pop: %i gen: %i 33 prosent done" %(filename, n, g)
        elif i == 20:
            print "%s 66 prosent done" % filename

    file = open(filename+".out", "a")
    output = "mean of 30 runs with pop %i and  generation of %i\n" %(n, g)
    output += "mean best fitness %f\n" %(total / 30.0)
    output += "genotype %s\n" %gap.best_solution
    output += "best fitness: %i\n" %gap.best_fitness
    output += "feasable: %s\n" %gap.feasible(gap.best_solution)
    output += "evaluations to best %i\n" %gap.evaluations_to_best
    file.write(output)
    file.close()
    print "%s done" % filename

@print_timing
def run_30_times_ga(filename):
    gap = GAP(filename, 50, 50, 10)
    total = 0.0
    for i in range(30):
        total += gap.run_ga()
    print "mean of 30 runs"
    print "mean best fitness %f" %(total / 30.0)
    print "genotype %s" %gap.best_solution
    print "best fitness: %i" %gap.best_fitness
    print "feasable: %s" %gap.feasible(gap.best_solution)
    print "evaluations to best %i" %gap.evaluations_to_best
    print "-------------------------------------------------"

    #solution = [0,0,2,1,0,2,0,0,1,1,0,2,2,2,1]
    #print gap.fitness(solution)

@print_timing
def run_10_times(filename):
    gap = GAP(filename, 100, 100, 100)
    total = 0.0
    for i in range(10):
        total += gap.run()
    print total / 10.0



N_values = []
N_values.append(10)
N_values.append(50)
N_values.append(100)
N_values.append(500)
generation_values = []
generation_values.append(10)
generation_values.append(50)
generation_values.append(100)
generation_values.append(500)


for n in N_values:
    for g in generation_values:
        thread.start_new_thread(run_30_times_chc,("data/D20-100.dat",n,g))
        #thread.start_new_thread(run_30_times_chc,("data/C10-100.dat",n,g))
        #thread.start_new_thread(run_30_times_chc,("data/C30-500.dat",n,g))
        #thread.start_new_thread(run_30_times_chc,("data/E10-100.dat",n,g))
        #thread.start_new_thread(run_30_times_chc,("data/E50-1000.dat",n,g))

data = input("waiting")

#run_30_times_ga('data/D3-15.dat')         # finding rand 46 iteration  , with repair 48
#run_30_times_chc('data/D3-15.dat')         # finding rand 46 iteration  , with repair 48

#run_30_times_ga('data/D20-100.dat')       # finding rand 495 iteration , with repair 336
#run_30_times_chc('data/D20-100.dat')       # finding rand 495 iteration , with repair 336

#run_30_times_ga('data/C10-100.dat')       # finding rand never         , with repair 999
#run_30_times_chc('data/C10-100.dat')       # finding rand never         , with repair 999


#run_30_times('data/C30-500.dat')       # finding rand never         , with repair 999
#run_30_times_chc('data/E10-100.dat')       # finding rand 50 iteration  , with repair 67
#run_30_times_chc('data/E50-1000.dat')      # finding rand never        , with repair 999


"""
Np 100, Nc 100, generations 100

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

mean of 30 runs
mean best fitness 18427.066667
genotype [1, 3, 3, 0, 0, 3, 7, 0, 0, 6, 5, 3, 5, 6, 6, 2, 1, 0, 5, 7, 3, 4, 2, 4, 2, 7, 7, 9, 3, 1, 3, 2, 1, 3, 9, 8, 5, 7, 4, 3, 2, 1, 6, 8, 9, 0, 3, 6, 0, 2, 8, 3, 5, 4, 7, 9, 9, 0, 1, 1, 5, 3, 2, 9, 2, 4, 8, 0, 6, 9, 7, 0, 7, 3, 2, 4, 4, 2, 4, 5, 2, 6, 0, 8, 5, 6, 5, 2, 4, 9, 3, 0, 3, 2, 4, 7, 8, 7, 7, 4]
best fitness: 17139
feasable: True
evaluations to best 170030
run_30_times took 53651.9999504 ms

mean of 30 runs
mean best fitness 235769.833333
genotype [14, 37, 35, 20, 49, 6, 36, 12, 1, 16, 14, 5, 11, 2, 17, 10, 26, 35, 44, 37, 41, 36, 42, 7, 30, 27, 14, 7, 14, 21, 10, 6, 40, 36, 16, 6, 30, 1, 23, 48, 34, 3, 4, 2, 32, 18, 27, 36, 49, 21, 38, 33, 1, 2, 10, 16, 15, 31, 2, 24, 37, 7, 5, 30, 12, 20, 22, 22, 6, 26, 30, 25, 33, 3, 29, 19, 5, 21, 10, 25, 48, 24, 18, 33, 25, 21, 43, 5, 12, 48, 2, 26, 29, 40, 33, 36, 41, 37, 6, 5, 46, 29, 36, 43, 33, 11, 10, 30, 41, 42, 9, 21, 18, 27, 10, 3, 20, 40, 33, 40, 25, 16, 12, 32, 10, 18, 36, 24, 29, 1, 46, 39, 28, 49, 43, 44, 0, 49, 29, 24, 30, 25, 39, 49, 7, 17, 2, 34, 0, 44, 38, 39, 3, 27, 45, 19, 20, 38, 47, 27, 21, 5, 40, 6, 21, 37, 33, 29, 5, 47, 2, 17, 4, 13, 35, 14, 1, 24, 48, 37, 20, 7, 10, 36, 19, 7, 1, 11, 4, 49, 13, 35, 0, 14, 18, 35, 17, 19, 17, 37, 1, 35, 6, 49, 38, 16, 9, 48, 37, 43, 17, 24, 46, 2, 0, 47, 25, 5, 13, 32, 41, 16, 1, 0, 4, 6, 6, 10, 37, 45, 24, 35, 44, 24, 29, 4, 13, 21, 6, 15, 27, 6, 10, 46, 28, 13, 11, 8, 49, 19, 41, 25, 0, 25, 17, 19, 41, 31, 3, 28, 24, 36, 33, 41, 13, 11, 6, 8, 49, 28, 47, 23, 23, 46, 17, 28, 24, 45, 27, 2, 27, 23, 35, 9, 49, 25, 44, 21, 3, 7, 24, 41, 46, 43, 5, 38, 17, 41, 40, 36, 46, 32, 7, 9, 13, 29, 13, 5, 13, 18, 19, 16, 25, 30, 34, 46, 15, 27, 44, 39, 24, 44, 31, 15, 21, 42, 35, 25, 39, 33, 27, 14, 18, 22, 22, 0, 21, 19, 9, 22, 11, 23, 15, 19, 22, 12, 46, 2, 5, 32, 23, 33, 38, 12, 8, 35, 36, 20, 20, 16, 13, 41, 35, 0, 0, 14, 37, 23, 5, 45, 41, 10, 21, 37, 17, 27, 25, 5, 18, 13, 13, 10, 36, 33, 27, 46, 0, 34, 47, 7, 8, 48, 48, 17, 25, 0, 49, 41, 7, 18, 37, 0, 4, 40, 20, 27, 31, 15, 19, 32, 17, 48, 37, 3, 16, 20, 8, 24, 22, 33, 33, 35, 27, 15, 10, 49, 0, 42, 3, 16, 41, 14, 27, 2, 8, 21, 46, 47, 8, 45, 20, 48, 45, 32, 2, 13, 43, 0, 42, 21, 22, 40, 23, 34, 33, 24, 29, 21, 1, 37, 1, 35, 44, 1, 7, 40, 38, 36, 30, 44, 4, 9, 20, 46, 13, 9, 8, 27, 47, 45, 30, 7, 1, 24, 37, 30, 30, 0, 1, 3, 21, 10, 36, 29, 7, 20, 1, 2, 31, 18, 43, 22, 18, 15, 8, 31, 33, 17, 2, 9, 3, 38, 22, 27, 37, 19, 48, 5, 10, 17, 19, 33, 24, 33, 30, 19, 21, 24, 31, 47, 47, 6, 41, 40, 32, 36, 6, 47, 49, 35, 34, 42, 31, 12, 45, 2, 22, 3, 17, 46, 19, 43, 8, 7, 22, 6, 30, 26, 47, 26, 8, 47, 39, 4, 24, 34, 38, 21, 28, 12, 5, 2, 10, 45, 44, 12, 21, 29, 0, 32, 31, 3, 34, 5, 43, 28, 21, 5, 36, 28, 4, 18, 9, 29, 42, 48, 33, 30, 1, 31, 34, 46, 1, 3, 18, 17, 10, 0, 18, 30, 37, 42, 48, 2, 25, 4, 5, 13, 42, 5, 6, 49, 7, 10, 7, 12, 7, 7, 21, 23, 29, 41, 9, 48, 1, 22, 14, 28, 21, 15, 37, 31, 45, 37, 16, 11, 31, 8, 28, 7, 8, 7, 9, 8, 46, 3, 46, 6, 8, 23, 31, 42, 32, 23, 34, 44, 15, 44, 9, 24, 0, 22, 10, 46, 1, 44, 33, 42, 31, 7, 29, 13, 40, 0, 0, 35, 24, 37, 9, 18, 9, 39, 44, 7, 13, 28, 5, 35, 2, 39, 7, 40, 29, 21, 9, 46, 24, 32, 4, 0, 16, 39, 11, 36, 14, 18, 32, 40, 26, 14, 21, 49, 2, 34, 21, 45, 40, 0, 13, 22, 10, 45, 15, 48, 39, 40, 37, 30, 29, 32, 46, 44, 31, 19, 21, 27, 39, 45, 48, 39, 46, 41, 21, 32, 12, 34, 29, 36, 30, 30, 35, 0, 43, 38, 16, 45, 48, 31, 32, 35, 11, 29, 45, 49, 39, 12, 48, 36, 18, 16, 29, 28, 35, 9, 29, 29, 39, 7, 35, 38, 10, 45, 42, 40, 43, 6, 2, 5, 3, 26, 1, 28, 31, 20, 13, 40, 4, 14, 39, 0, 49, 34, 29, 42, 6, 14, 29, 26, 40, 13, 34, 43, 16, 28, 33, 27, 39, 15, 32, 27, 27, 4, 13, 44, 47, 30, 35, 9, 15, 43, 6, 32, 2, 22, 2, 20, 35, 45, 37, 36, 4, 43, 41, 36, 26, 12, 42, 7, 7, 9, 8, 6, 6, 3, 38, 2, 3, 44, 43, 23, 26, 26, 26, 36, 41, 40, 29, 42, 3, 11, 9, 34, 28, 32, 13, 37, 29, 39, 18, 37, 36, 33, 41, 15, 47, 6, 4, 49, 12, 30, 28, 6, 10, 43, 22, 13, 13, 49, 30, 42, 49, 20, 22, 31, 29, 41, 38, 11, 45, 32, 40, 40, 18, 2, 39, 39, 49, 23, 13, 26, 9, 38, 20, 20, 34, 48, 15, 39, 41, 42, 30, 47, 49, 49, 45, 3, 41, 4, 43, 5, 42, 28, 26, 16, 19, 30, 18, 20, 24, 35, 45, 32, 15, 4, 11, 43, 26, 34, 2, 30, 3, 37, 4, 42, 4, 3, 13, 49, 26, 32, 15, 15, 15, 29, 20, 32, 43, 13, 32, 28, 28, 41, 4, 31, 8, 15, 40, 48, 2, 9]
best fitness: 234043
feasable: False
evaluations to best 190096
run_30_times took 2215671.0 ms
"""



