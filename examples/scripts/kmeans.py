# Author: Korobka A.

from Pyro4 import expose
import numpy as np

class Solver:
    def __init__(self, workers=None, input_file_name=None, output_file_name=None):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.workers = workers
        print("Inited")

    def get_closest_centroids_par(self, centroids):
        chunks = np.split(self.X, len(self.workers))
        # map
        mapped = []
        c = centroids.tolist()
        for i in xrange(0, len(self.workers)):
            l = chunks[i].tolist()
            mapped.append(self.workers[i].get_closest_centroids(l, c))

        print('Map finished: ', mapped)

        # reduce
        reduced = self.myreduce(mapped)
        print("Reduce finished: " + str(reduced))
        # output
        return reduced

        print("Job Finished")

    def solve(self):
        print("Job Started")
        print("Workers %d" % len(self.workers))
        self.read_input()
        self.initial_centroids = self._init_centroids(self.X)
        centroids = np.asarray(self.initial_centroids)
        objective_history = []
        convergence = False
        iteration = 0
        while not convergence:
            closest_centroids = self.get_closest_centroids_par(centroids)
            centroids = self._move_centroids(closest_centroids)
            objective = self._kmeans_objective(centroids, closest_centroids)
            objective_history.append(objective)
            iteration += 1
            convergence = len(objective_history) > 2 and (
                    objective_history[-2] / objective_history[-1] < 1.01 or iteration > self.max_iter)
            print("Iteration: {0:2d}    Objective: {1:.3f}".format(iteration, objective))
        print("Job Finished")
        self.write_output(closest_centroids)

    def _init_centroids(self, X):
        return np.asarray([X[i] for i in np.random.choice(range(0, len(X)), self.num_clusters, replace=False)])

    @staticmethod
    @expose
    def get_closest_centroids(X, centroids):
        X = np.asarray(X)
        centroids = np.asarray(centroids)
        res = [np.argmin([np.sum(np.power(x - c, 2)) for c in centroids]) for x in X]
        return [np.asscalar(x) for x in res]

    @staticmethod
    def myreduce(mapped):
        output = []
        for x in mapped:
            output += x.value
        print(output)
        return output
        
    def _move_centroids(self, closest_centroids):
        res = np.zeros((self.num_clusters, self.X.shape[-1]))
        for i in range(self.num_clusters):
            assigned_points = self.X[closest_centroids == i]
            res[i] = np.mean(assigned_points, axis=0)
        return res

    def _kmeans_objective(self, centroids, closest_centroids):
        cost_sum = 0
        for i in range(len(centroids)):
            assigned_points = self.X[closest_centroids == i]
            cost_sum += np.sum(np.power(assigned_points - centroids[i], 2))
        return cost_sum

    def read_input(self):
        f = open(self.input_file_name, 'r')
        self.num_clusters = int(f.readline())
        self.X = []
        for line in f:
            self.X.append([float(l) for l in line.split()])
        self.X = np.array(self.X)
        f.close()

    def write_output(self, closest_centroids):
        f = open(self.output_file_name, 'w')
        for i in range(self.num_clusters):
             f.write(self.X[closest_centroids == i])
             f.write('\n')
        f.close()
