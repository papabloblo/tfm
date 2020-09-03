#from Neighborhood import Neighborhood
import time
import json

class VNS:
    def __init__(self, collection, path, epsilon=False, max_time=240):
        self.iter = 0
        self.best_collection = collection.copy()
        self.candidate_collection = collection.copy()
        self.candidate_collection2 = collection.copy()
        self.path = path

        self.neighbor_k = 0
        self.neighbor_random_k = 0
        self.epsilon = epsilon
        self.max_time = max_time*60

    def epsilon_change(self):
        epsilon = 0
        if self.epsilon:
            # epsilon = max(0, (300 - self.iter) / 300)
            epsilon = 10/(1+0.0005*(self.iter**2))

        print(epsilon)
        return epsilon

    def random_neighbor(self):
        if self.neighbor_random_k == 0:
            self.candidate_collection.add_random()
        elif self.neighbor_random_k == 1:
            self.candidate_collection.swap_random()
        elif self.neighbor_random_k == 2:
            self.candidate_collection.change_random()
        else:
            raise Exception('Invalid k', k)

        self.candidate_collection2 = self.candidate_collection.copy()


    def update_neighbor_k(self):
        if self.candidate_collection.waste_collected() <= self.candidate_collection2.waste_collected() + self.epsilon_change() \
                or not self.candidate_collection.time_constraint():
            if self.candidate_collection.waste_collected() > self.candidate_collection2.waste_collected() \
                    and self.candidate_collection.time_constraint():

                self.candidate_collection2 = self.candidate_collection.copy()
            else:

                self.candidate_collection = self.candidate_collection2.copy()
            self.neighbor_k += 1
        else:

            self.candidate_collection2 = self.candidate_collection.copy()
            self.neighbor_k = 0

    def update_neighbor_random_k(self):
        if self.candidate_collection.waste_collected() <= self.best_collection.waste_collected() + self.epsilon_change() \
                or not self.candidate_collection.time_constraint():

            if self.candidate_collection.waste_collected() > self.best_collection.waste_collected() \
                    and self.candidate_collection.time_constraint():

                self.best_collection = self.candidate_collection.copy()


            self.candidate_collection = self.best_collection.copy()

            self.neighbor_random_k += 1
        else:
            self.best_collection = self.candidate_collection.copy()
            self.best_collection.waste_add = self.candidate_collection.waste_add
            self.neighbor_random_k = 0

    def neighborhood_k(self):
        self.iter += 1
        print(self.iter)
        if self.neighbor_k == 0:
            print("Neighborhood: add")
            self.candidate_collection.add_best()
        elif self.neighbor_k == 1:
            print("Neighborhood: swap")
            self.candidate_collection.swap_best()
        elif self.neighbor_k == 2:
            print("Neighborhood: change")
            self.candidate_collection.change_best()

        else:
            raise Exception('Invalid k', k)


    def VND(self, k_max):
        self.neighbor_k = 0
        while self.neighbor_k <= k_max and self.execution_time() < self.max_time:

            self.neighborhood_k()

            self.update_neighbor_k()
            print("Total time:", round((time.time() - self.ini_time)/60, 2), "minutes")

            self.print()
            print()

            self.log()

    def GVNS(self, l_max, k_max, t_max):
        self.ini_time = time.time()
        t = 0
        while t < t_max and self.execution_time() < self.max_time:
            print('Iteración', t)
            self.neighbor_random_k = 0
            while self.neighbor_random_k < k_max and self.execution_time() < self.max_time:
                self.neighbor_k = 0
                self.random_neighbor()
                self.print()
                self.VND(k_max=l_max)
                self.update_neighbor_random_k()
            t += 1
        print('End')
        #return t


    def execution_time(self):
        return time.time() - self.ini_time

    def print(self, best=False):
        if best:
            candidate = self.best_collection
        else:
            candidate = self.candidate_collection
        max_waste = sum([candidate.waste_collection.fill_rate[p] * candidate.horizon + candidate.waste_collection.fill_ini[p] for p in candidate.waste_collection.fill_rate.keys()])
        waste_day = candidate.mean_waste_h()
        waste_day = [round(x, 3) for x in waste_day]
        long = [len(r) for r in candidate.routes()]
        best_waste = self.best_collection.waste_collected()
        print()
        print('Total waste collected', round(candidate.waste_collected(), 2), "(",
              round(candidate.waste_collected() / max_waste * 100, 2), "%)")
        print('Best waste collected:', round(best_waste, 2))

        a = {p: candidate.waste_collected_point_h2(p, candidate.h_with_point(p)) for p in candidate.unique_points()}
        mi = []
        for i in a.values():
            mi += list(i.values())

        print()
        print('Mean fill level: ', round(sum(mi)*100 / len(mi), 2), "%")
        print("Containers:", sum(long))
        print("Containers by day:", sum(long)/len(long))
        tiempo = [round(ti / 3600, 2) for ti in candidate.time_h()]

        print()
        for h in range(candidate.horizon):
            print("Day", str(h) + ":", long[h], "pickup points in", tiempo[h], "hours.", "Mean waste: ", waste_day[h])

    def log(self):
        x = {
            "iter": self.iter,
            "best_waste": self.best_collection.waste_collected(),
            "candidate1_waste": self.candidate_collection.waste_collected(),
            "candidate2_waste": self.candidate_collection.waste_collected(),
            "best": [[int(r2) for r2 in r] for r in self.best_collection.routes()],
            "candidate": [[int(r2) for r2 in r] for r in self.candidate_collection.routes()],
            "candidate2": [[int(r2) for r2 in r] for r in self.candidate_collection2.routes()],
            "time": time.time() - self.ini_time
        }
        f = open(self.path, "a")
        f.write(json.dumps(x) + '\n')
        f.close()



