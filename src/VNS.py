
class VNS:
    def __init__(self, collection):
        self.collection = collection
        self.neighborhood = Neighborhood(self.collection)

        self.size = 50
        self.random_size = 500
        self.iter = 0

    def random_neighbor(self, k):
        if k == 0:
            return self.neighborhood.random_swap_point()
        elif k == 1:
            return self.neighborhood.random_add_point()
        elif k == 2:
            return self.neighborhood.random_change_point()
        elif k == 3:
            return self.neighborhood.random_remove()
        else:
            raise Exception('Invalid k', k)

    def neighborhood_change(self, current_collection, new_collection, k):
        if new_collection.waste_collected() > current_collection.waste_collected():
            return {'new_route': new_collection, 'k': 0}
        else:
            return {'new_route': current_collection, 'k': k + 1}

    def neighborhood_k(self, current_collection, k):
        ini_neigh = time.time()
        self.iter += 1
        print(self.iter)
        if k == 0:
            print("Add")
            new = self.neighborhood.add_best_neighbors(current_collection)
        elif k == 1:
            print("Swap")
            new = self.neighborhood.swap_best_neighbors(current_collection)
        elif k == 2:
            print("Change")
            new = self.neighborhood.change_best_neighbors(current_collection)
        elif k == 3:
            print("Remove")
            new = self.neighborhood.remove_best_neighbors(current_collection)
        else:
            raise Exception('Invalid k', k)

        print("Fin en", (time.time() - ini_neigh), "(", round((time.time() - ini_neigh) / 60, 2), "minutos", ")")
        return new

    def VND(self, current_collection, k_max):
        k = 0
        while k < k_max:

            new_collection = self.neighborhood_k(current_collection, k)

            neigh_change = self.neighborhood_change(current_collection, new_collection, k)

            current_collection = neigh_change['new_route']
            k = neigh_change['k']

            print("Tiempo:", round((time.time() - self.ini_time)/60, 2), "minutos")
            self.print(current_collection)
            print()

        return current_collection


    def GVNS(self, l_max, k_max, t_max):
        self.ini_time = time.time()
        t = 0
        while t < t_max:
            print('Iteración', t)
            k = 0
            while k < k_max:
                if self.iter > 0:
                    x = self.random_neighbor(k)
                else:
                    x = self.collection
                x2 = self.VND(x, k_max=l_max)
                neigh_change = self.neighborhood_change(x, x2, k)
                if self.collection.time_constraint(neigh_change['new_route']) :
                    self.collection = neigh_change['new_route']
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

