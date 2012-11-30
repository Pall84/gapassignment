__author__ = 'Palli'
from random import randrange
from sys import maxint

def mysplit(s, delim=None):
    """ returns string split without delim
        taken from http://stackoverflow.com/questions/2197451/why-are-empty-strings-returned-in-split-results
    """
    return [x for x in s.split(delim) if x]


class GAP:
    def __init__(self, filename):

        self.best_fitness = maxint
        self.best_genome = None

        # open data file
        file = open(filename, "r")

        # read document
        doc = file.read()

        # split document into paragraphs
        paragraphs = mysplit(doc, "\n\n")

        # number of agents, tasks
        line = paragraphs[1]
        words = mysplit(line, " ")
        self.number_of_agents = int(words[0])
        self.number_of_tasks = int(words[1])

        # agents capacity
        line = paragraphs[2]
        words = mysplit(line, " ")
        self.agents_max_capacity = []
        for i in range(self.number_of_agents):
            self.agents_max_capacity.append(int(words[i]))

        # resource matrix
        self.resource_matrix = []
        lines = mysplit(paragraphs[3], "\n")
        for i in range(self.number_of_agents):
            words = mysplit(lines[i], " ")
            resource_line = []
            for j in range(self.number_of_tasks):
                resource_line.append(int(words[j]))
            self.resource_matrix.append(resource_line)

        # cost matrix
        self.cost_matrix = []
        lines = mysplit(paragraphs[4], "\n")
        for i in range(self.number_of_agents):
            words = mysplit(lines[i], " ")
            cost_line = []
            for j in range(self.number_of_tasks):
                cost_line.append(int(words[j]))
            self.cost_matrix.append(cost_line)

    def __random_population(self):
        genome = []
        for task in range(self.number_of_tasks):
            agent = randrange(self.number_of_agents)
            genome.append(agent)
        return genome

    def __random_population_repair(self):
            genome = []
            agents_capacity = self.agents_max_capacity[:]
            for task in range(self.number_of_tasks):
                j = 0
                while j  < 500:
                    agent = randrange(self.number_of_agents)
                    resource = self.resource_matrix[agent][task]
                    if resource <= agents_capacity[agent]:
                        genome.append(agent)
                        agents_capacity[agent] -= resource
                        break
                    else:
                        j += 1
                else:
                    return None
            return genome

    def __random_populations(self, N):
        pop = []
        for i in range(N):
            for tries in range(self.number_of_tasks*2):
                genome = self.__random_population_repair()
                if genome:
                    pop.append(genome)
                    break
        for j in range(len(pop)-N):
            genome = self.__random_population()
            pop.append(genome)
        return pop

    def __random_parents(self, P):
        random_parent = randrange(len(P))
        p1 = P[random_parent]
        P.remove(p1)
        random_parent = randrange(len(P))
        p2 = P[random_parent]
        P.remove(p2)
        return p1, p2

    def __distance(self, p1_p2):
        dist = 0
        for gene in range(len(p1_p2[0])):
            if p1_p2[0][gene] != p1_p2[1][gene]:
                dist += 1
        return dist

    def __hux(self, p1_p2):
        c1 = []
        c2 = []
        p1_max_swap = self.__distance(p1_p2)/2
        for gene in range(len(p1_p2[0])):
            p1_first = randrange(2)
            if p1_p2[0][gene] == p1_p2[1][gene] or ( p1_first and p1_max_swap > 0):
                c1.append(p1_p2[0][gene])
                c2.append(p1_p2[1][gene])
                p1_max_swap += 1
            else:
                c1.append(p1_p2[1][gene])
                c2.append(p1_p2[0][gene])
        return c1, c2

    def __evaluate(self, genome):
        fitness = self.fitness(genome)
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_genome = genome
        return fitness

    def fitness(self, genome):
        if not self.__feasible(genome):
            return maxint
        else:
            fitness = 0
            for task in range(len(genome)):
                agent = genome[task]
                cost = self.cost_matrix[agent][task]
                fitness += cost
            return fitness

    def __fitness_compare(self,a, b):
        fitness_a = self.fitness(a)
        fitness_b = self.fitness(b)
        if fitness_a > fitness_b:
            return 1
        elif fitness_a == fitness_b:
            return 0
        else:
            return -1

    def __feasible(self, genome):
        if not genome:
            return False
        agents_capacity = self.agents_max_capacity[:]
        for task in range(len(genome)):
            agent = genome[task]
            resource = self.resource_matrix[agent][task]
            if resource <= agents_capacity[agent]:
                agents_capacity[agent] -= resource
            else:
                return False
        return True

    def __diverge(self, P):
        best_genome = self.__find_best(P)

        P_new = []
        for index in range(len(P)):
            genome = best_genome[:]
            for rate in range(len(P)/3):
                rand_gene = randrange(len(genome))
                rand_flip = randrange(self.number_of_agents)
                genome[rand_gene] = rand_flip
            P_new.append(genome)
        return P_new

    def __find_best(self, P):
        best_fitness = maxint
        best_genome = P[randrange(len(P))]
        for genome in P:
            fitness = self.fitness(genome)
            if fitness < best_fitness:
                best_fitness = fitness
                best_genome = genome
        return best_genome

    def __replace(self, N, P, C):
        P_C = P+C
        P_C.sort(self.__fitness_compare)
        temp = P_C[:N]
        for genome in temp:
            self.__evaluate(genome)
        return temp

    def evolve(self, Np, generations):
        L = self.number_of_tasks
        N = Np
        P = self.__random_populations(N)
        if len(P) <= 1:
            print "done"
        Thresh = L/4
        for generation in range(generations):
            C = []
            P_copy = P[:]
            for i in range(N/2):
                if len(P_copy) <= 1:
                    print "done"
                #print len(P_copy)
                p1_p2 = self.__random_parents(P_copy)
                if self.__distance(p1_p2) >= Thresh:
                    c1_c2 = self.__hux(p1_p2)
                    self.__evaluate(c1_c2[0])
                    self.__evaluate(c1_c2[1])
                    C.append(c1_c2[0])
                    C.append(c1_c2[1])

            if len(C) <= 0:
                L -= 1
                if L <= 0:
                    P = self.__diverge(P)
                    if len(P) < N:
                        print "done"
                    L = self.number_of_tasks
            else:
                P = self.__replace(N, P, C)
                if len(P) < N:
                    print "done"

def run_30_times(filename, n, g):
    gap = GAP("data/"+filename)
    mean_fitness = 0
    best_fitness = maxint
    best_genome = None
    for i in range(30):
        gap.evolve(n, g)
        mean_fitness += gap.best_fitness

    msg = "%s\n%s : %s\n%s\n" %(filename, n, g, mean_fitness/30.0)
    file = open("data/"+filename+".out", "a")
    file.write(msg)
    file.close()


N = []
N.append(10)
N.append(50)
N.append(100)
N.append(500)
N.append(1000)
N.append(5000)
N.append(10000)

for n in N:
    for g in N:
        run_30_times("C10-100.dat", n, g)
