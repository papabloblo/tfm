#from Neighborhood import Neighborhood
import time
import json

class VNS:
    def __init__(self, collection, path):
        self.iter = 0
        self.best_collection = collection.copy()
        self.candidate_collection = collection.copy()
        self.candidate_collection2 = collection.copy()
        self.path = path

        self.neighbor_k = 0
        self.neighbor_random_k = 0
        self.epsilon = 0.05

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
        if self.candidate_collection.waste_collected() <= self.candidate_collection2.waste_collected() + self.epsilon \
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
        if self.candidate_collection.waste_collected() <= self.best_collection.waste_collected() + self.epsilon \
                or not self.candidate_collection.time_constraint():
            self.candidate_collection = self.best_collection.copy()
            self.neighbor_random_k += 1
        else:
            self.best_collection = self.candidate_collection.copy()
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
        while self.neighbor_k <= k_max:
            self.neighborhood_k()
            self.update_neighbor_k()
            print("Total time:", round((time.time() - self.ini_time)/60, 2), "minutes")
            self.print()
            print()
            #self.log()

    def GVNS(self, l_max, k_max, t_max):
        self.ini_time = time.time()
        t = 0
        while t < t_max:
            print('Iteración', t)
            self.neighbor_random_k = 0
            while self.neighbor_random_k < k_max:
                self.neighbor_k = 0
                self.random_neighbor()
                self.print()
                self.VND(k_max=l_max)
                self.update_neighbor_random_k()
            t += 1
        return t

    def print(self):
        max_waste = sum([self.candidate_collection.waste_collection.fill_rate[p] * self.candidate_collection.horizon + self.candidate_collection.waste_collection.fill_ini[p] for p in self.candidate_collection.waste_collection.fill_rate.keys()])
        waste_day = self.candidate_collection.mean_waste_h()
        waste_day = [round(x, 3) for x in waste_day]

        print()
        print('Total waste collected', round(self.candidate_collection.waste_collected(), 2), "(",
              round(self.candidate_collection.waste_collected() / max_waste * 100, 2), "%)")

        tiempo = [round(ti / 3600, 2) for ti in self.candidate_collection.time_h()]
        long = [len(r) for r in self.candidate_collection.routes()]
        print()
        for h in range(self.candidate_collection.horizon):
            print("Day", str(h) + ":", long[h], "pickup points in", tiempo[h], "hours.", "Mean waste: ", waste_day[h])

    def log(self):
        x = {
            "iter": self.iter,
            "waste_collected": self.candidate_collection.waste_collected(),
            "total_time": time.time() - self.ini_time,
            "time": 10,
            "neighborhood": "add",
            "route": [[int(r2) for r2 in r] for r in self.candidate_collection.routes()]
        }
        f = open(self.path+"/log.txt", "a")
        f.write(json.dumps(x) + '\n')
        f.close()



