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
                if solution:
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

    def evaluate(self, solution):
        self.evaluations += 1
        fitness = self.fitness(solution)
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_solution = copy(solution)
            self.evaluations_to_best = self.evaluations
        return fitness

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
        new_pop.append(best_member)
        pop_size = len(P)
        for index in range(pop_size-1):
            new_member = copy(best_member)
            for run in range(self.number_of_tasks/3):
                random_flip = randrange(self.number_of_agents)
                random_gene = randrange(self.number_of_tasks)
                new_member[random_gene] = random_flip
            new_pop.append(new_member)
        return new_pop


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
                    P = self.diverge(P)
                    L = self.number_of_tasks
            else:
                P = self.replace(N, P, C)
        return self.best_fitness

@print_timing
def run_30_times_chc(filename,n,g):
    gap = GAP(filename, n, g)
    total = 0.0
    best_genotype = None
    best_fitness = sys.maxint
    evaluations_to_best = 0
    for i in range(30):
        total += gap.run_chc()
        if gap.best_fitness < best_fitness:
            best_fitness = gap.best_fitness
            best_genotype = gap.best_solution
            evaluations_to_best = gap.evaluations_to_best
        if i == 10:
            print "%s pop: %i gen: %i 33 prosent done" %(filename, n, g)
        elif i == 20:
            print "%s pop: %i gen: %i 66 prosent done" %(filename, n, g)

    #file = open(filename+".out", "a")
    output = "mean of 100 runs with pop %i and  generation of %i\n" %(n, g)
    output += "mean best fitness %f\n" %(total / 30.0)
    output += "genotype %s\n" %best_genotype
    output += "best fitness: %i\n" %best_fitness
    output += "feasable: %s\n" %gap.feasible(best_genotype)
    output += "evaluations to best %i\n" %evaluations_to_best
    #file.write(output)
    #file.close()
    #print "%s pop: %i gen: %i done" %(filename, n, g)
    print output


#run_30_times_chc("data/C10-100.dat",10, 10)
#run_30_times_chc("data/C30-500.dat",10, 10)
#run_30_times_chc("data/D3-15.dat",10, 10)
#run_30_times_chc("data/D20-100.dat",10, 10)
#run_30_times_chc("data/E10-100.dat",10, 10)
run_30_times_chc("data/E50-1000.dat",10, 10)
