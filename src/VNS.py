#from src.Neighborhood import Neighborhood

class VNS(Neighborhood):
    def __init__(self, collection):
        super().__init__(collection, collection)
        self.iter = 0
        self.best_collection = self.collection.copy()

    def random_neighbor(self, k):
        self.tabu_list = {}
        if k == 0:
            random_collection = self.random_add_point()
        elif k == 1:
            random_collection = self.random_remove()
        elif k == 2:
            random_collection = self.random_change_point()
        elif k == 3:
            random_collection = self.random_swap_point()
        else:
            raise Exception('Invalid k', k)
        if not random_collection.time_constraint():
            random_collection = self.fix_time_constraint(random_collection)

        return random_collection


    def neighborhood_change(self, current_collection, new_collection, k):


        if new_collection.waste_collected() <= current_collection.waste_collected() or not current_collection.time_constraint():

                return {'new_route': current_collection, 'k': k + 1}

        elif new_collection.waste_collected() - current_collection.waste_collected() < 0.01:
            return {'new_route': new_collection, 'k': k + 1}
        else:
            return {'new_route': new_collection, 'k': 0}


    def neighborhood_k(self, k):
        ini_neigh = time.time()
        self.iter += 1
        print(self.iter)
        if k == 0:
            print("Add")
            new = self.add_best_neighbors()
        elif k == 1:
            print("Change")
            new = self.change_best_neighbors()
        elif k == 2:
            print("Swap")
            new = self.swap_best_neighbors()
        elif k == 3:
            print("Remove")
            new = self.remove_best_neighbors()
        else:
            raise Exception('Invalid k', k)
        duration = time.time() - ini_neigh
        print("Fin en", round(duration, 2), "(", round(duration/60, 2), "minutos", ")")
        return new

    def VND(self, k_max):
        k = 0
        while k <= k_max:

            new_collection = self.neighborhood_k(k)
            neigh_change = self.neighborhood_change(self.collection, new_collection, k)
            self.collection = neigh_change['new_route']
            #self.neighborhood.collection = neigh_change['new_route']
            k = neigh_change['k']

            print("Tiempo:", round((time.time() - self.ini_time)/60, 2), "minutos")
            self.print(self.collection)
            print()

            self.update_tabu_list()


    def GVNS(self, l_max, k_max, t_max):
        self.ini_time = time.time()
        t = 0
        while t < t_max:
            print('Iteración', t)
            k = 0
            while k < k_max:
                #if self.iter > 0:
                x = self.random_neighbor(k)
                self.collection = x.copy()
                    #self.neighborhood.collection = self.collection
                #else:
                 #   x_orig = self.collection.copy()
                self.VND(k_max=l_max)
                neigh_change = self.neighborhood_change(self.best_collection, self.collection, k)
                if self.collection.time_constraint():
                    self.collection = neigh_change['new_route']
                    self.best_collection = self.collection.copy()
                    #self.neighborhood.collection = neigh_change['new_route']
                else:
                    self.collection = self.best_collection.copy()
                k = neigh_change['k']
                print(self.collection.waste_collected())
            t += 1
        return t

    def print(self, current_collection):
        max_mierda = sum([i * 7 for i in self.collection.waste_collection.fill_rate.values()])
        print('Mierda recogida', round(current_collection.waste_collected(), 2), "(",
              round(current_collection.waste_collected() / max_mierda * 100, 2), "%)")


        tiempo = [round(ti / 3600, 2) for ti in current_collection.time_h()]
        long = [len(r) for r in current_collection.routes()]
        for h in range(self.collection.horizon):
            print("Día", str(h) + ":", long[h], "puntos en", tiempo[h], "horas")

