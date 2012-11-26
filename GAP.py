__author__ = 'Palli'
import random
import sys

class GAP:
    def __init__(self, filename):

        self.Np = 100
        self.Nc = 100

        self.number_of_agents = 0
        self.number_of_tasks = 0
        self.agents_capacity = []
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
            self.agents_capacity.append(int(capacity))

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

    def fitness(self, solution):
        fitness = 0
        for task_nr in range(self.number_of_tasks):
            agent_nr = solution[task_nr]
            fitness += self.cost_matrix[agent_nr][task_nr]

        return fitness

    def over_worked(self, solution):
        agents =[]
        for i in range(self.number_of_agents):
            agents.append(0)
        for task_nr in range(self.number_of_tasks):
            agent_nr = solution[task_nr]
            agents[agent_nr] += self.resource_matrix[agent_nr][task_nr]

        for i in range(self.number_of_agents):
            if agents[i] > self.agents_capacity[i]:
                return True

        return False

    def __random_solution(self):
        solution = []
        for i in range(self.number_of_tasks):
            solution.append(random.randrange(self.number_of_agents))
        if self.over_worked(solution):
            return self.__random_solution()
        else:
            return solution

    def random_solution(self, nr_of_solution):
        solutions = []
        for i in range(nr_of_solution):
            solutions.append(self.__random_solution())
        return solutions

    def tournament_selection(self, k, pop):
        selections = []
        for i in range(k):
            selections.append(pop[random.randrange(len(pop))])

        fittest = None
        for selection in selections:
            if fittest == None:
                fittest = selection
            elif self.fitness(fittest) > self.fitness(selection):
                fittest = selection

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
        fitness = self.fitness(solution)
        if fitness < self.best_fitness:
            self.best_fitness = fitness
            self.best_solution = solution

    def run(self):
        self.pop = self.random_solution(self.Np)

        for i in range(100):
            cpop = []
            while len(cpop) < self.Nc:
                p1 = self.tournament_selection(2, self.pop)
                p2 = self.tournament_selection(2, self.pop)

                c1 = self.uniform_crossover(p1,p2)
                c2 = self.uniform_crossover(p1,p1)

                self.evaluate(c1)
                self.evaluate(c2)

                cpop.append(c1)
                cpop.append(c2)

            self.pop = cpop


#gap = GAP('data/D3-15.dat')
#gap.run()

#print gap.best_fitness
#print gap.best_solution

gap = GAP('data/D3-15.dat')
gap.run()

print gap.best_fitness
print gap.best_solution

solution = [0,0,2,1,0,2,0,0,1,1,0,2,2,2,1]
print gap.fitness(solution)