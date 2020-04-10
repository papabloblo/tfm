import pandas as pd
import random
import numpy as np

class Neighborhood:

    def points_h_available(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection

        tabu = n.tabu_list()
        h = {}
        for p in n.pickup_points:
            h_aux = set(new_collection.h_without_point(p))
            if p in tabu.keys():
                h_aux = h_aux.difference(set(tabu[p]))
            h_aux = list(h_aux)
            h_aux.sort()
            if len(h_aux) > 0:
                h[p] = h_aux
        p_random = np.random.choice(list(h.keys()), replace=False, size=min(self.random_size, len(h)))
        h = {p: h2 for p, h2 in h.items() if p in p_random}
        return h

    def points_add_h_available(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection
        tabu = self.tabu_list()
        h = {}
        for p in self.pickup_points:
            h_aux = set(new_collection.point_h_available(p))
            if p in tabu.keys():
                h_aux = h_aux.difference(set(tabu[p]))
            h_aux = list(h_aux)
            h_aux.sort()
            if len(h_aux) > 0:
                h[p] = h_aux
        return h

    def waste_add(self, new_collection=None):
        w = {'point': [], 'h': [], 'waste': []}
        points_h_available = self.points_add_h_available(new_collection)
        for p, h in points_h_available.items():
            h_w = new_collection.add_point_waste_collected(p, h=h)
            w['point'] += [p]*len(h_w)
            w['h'] += h_w.keys()
            w['waste'] += h_w.values()

        w = pd.DataFrame(w)
        w.sort_values(by=['waste'], inplace=True, ascending=False)
        return w

    def add_best_neighbors(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection

        w = n.waste_add(new_collection)
        routes = new_collection.routes()

        new_routes = []
        count_neighbors = 0
        for waste in w['waste'].unique():
            w_aux = w[w['waste'] == waste]
            for i in range(len(w_aux)):
                count_neighbors += 1
                point = w_aux.iloc[i, 0]
                h = w_aux.iloc[i, 1]
                for pos in range(len(routes[h]) - 1):
                    new_route = new_collection.copy()
                    new_route.add_point(point, h, pos)

                    new_routes.append(new_route)
            new_routes = new_collection.filter_routes_time_constraint(new_routes)
            if len(new_routes) > 0:
                break

        return new_routes

    def random_add_point(self):
        points_h_available = self.points_h_available()
        new_route = self.collection.copy()

        random_point = random.choice(list(points_h_available.keys()))
        random_h = random.choice(points_h_available[random_point])

        route = self.collection.routes()[random_h]
        position = random.choice(range(len(route) - 1))

        new_route.add_point(random_point, random_h, position)

        return new_route

    def random_change_point(self):
        new_route = self.collection.copy()
        routes = new_route.routes()

        points_h_available = self.points_h_available()
        h2 = [h2 for h2, r in enumerate(self.collection.routes()) if len(r) > 2]
        h2 = set(h2)
        points_h_available = {p: list(h2.intersection(set(h))) for p, h in points_h_available.items()}
        points_h_available = {p: h for p, h in points_h_available.items() if len(h) > 0}

        if len(points_h_available) > 0:
            random_point = random.choice(list(points_h_available.keys()))

            random_h = random.choice(points_h_available[random_point])

            route = routes[random_h]
            position = random.choice(range(1, len(route) - 1))

            new_route.change_point(random_point, random_h, position)

        return new_route

    def random_remove(self):
        new_route = self.collection.copy()
        routes = new_route.routes()
        h = [h for h in range(len(routes)) if len(routes[h]) > 2]
        random_h = random.choice(h)
        random_position = random.choice(range(1, len(routes[random_h])-1))

        new_route.collection[random_h].remove_point(random_position)

        return new_route

    def change_best_neighbors(self, new_collection = None):
        if new_collection is None:
            new_collection = self.collection()

        routes = new_collection.routes()

        points_h_available = self.points_h_available()
        h2 = [h2 for h2, r in enumerate(new_collection.routes()) if len(r) > 2]
        h2 = set(h2)
        points_h_available = {p: list(h2.intersection(set(h))) for p, h in points_h_available.items()}
        points_h_available = {p: h for p, h in points_h_available.items() if len(h) > 0}

        new_routes = []
        if len(points_h_available) > 0:
            for p, h in points_h_available.items():
                for h2 in h:
                    for pos in range(1, len(routes[h2]) - 1):
                        new_route = new_collection.copy()
                        new_route.change_point(p, h2, pos)
                        new_routes.append(new_route)

            new_routes = new_collection.filter_routes_time_constraint(new_routes)
            w = [r.waste_collected() for r in new_routes]
            if len(w) > 0:
                max_w = max(w)
                new_routes = [r for r in new_routes if r.waste_collected() == max_w]
            else:
                new_routes = [new_collection]
        return new_routes

    def remove_best_neighbors(self, new_collection = None):
        if new_collection is None:
            new_collection = self.collection()

        routes = new_collection.routes()

        new_routes = []
        for h in range(7):
            if len(routes[h]) > 2:
                for pos in range(1, len(routes[h]) - 1):
                    new_route = new_collection.copy()
                    new_route.remove_point(h, pos)
                    new_routes.append(new_route)

            new_routes = new_collection.filter_routes_time_constraint(new_routes)
            w = [r.waste_collected() for r in new_routes]
            if len(new_routes) > 0:
                max_w = max(w)
                new_routes = [r for r in new_routes if r.waste_collected() == max_w]


        return new_routes

class TabuSearch(Neighborhood):
    def __init__(self, horizon, collection):
        self.size = 50
        self.collection = collection
        self.horizon = horizon
        self.pickup_points = collection.waste_collection.pickup_points
        self._tabu_list = self.initialize_tabu_list()
        self.random_size = 500



    def initialize_tabu_list(self):
        #h = dict.fromkeys(range(7), None)
        #return {p: {h: random.choice(range(0, self.size + 1)) for h in range(self.horizon)} for p in self.pickup_points}
        h = {h: None for h in range(self.horizon)}
        #h = {0:self.size + 1, 1: 0, 2: 0, 3:0, 4:0, 5:0, 6: self.size+1}
        return {p: h.copy() for p in self.pickup_points}

    def update_tabu_list(self, prev_route, new_route):

        for h, r in enumerate(new_route):
            for p in self.pickup_points:
                if p in r and p not in prev_route[h]:
                    self._tabu_list[p][h] = 0
                elif self._tabu_list[p][h] is not None:
                    self._tabu_list[p][h] += 1

    def tabu_list_old(self):
        tabu_list = {}
        for p, h in self._tabu_list.items():
            tabu_list[p] = [h2 for h2, tabu in h.items() if tabu is not None and tabu < self.size]
            if len(tabu_list[p]) == 0:
                del tabu_list[p]
        return tabu_list


    def tabu_list(self):
        tabu_list = {}
        for p, h in self._tabu_list.items():
            tabu_list[p] = [h2 for h2, tabu in h.items() if tabu is not None and tabu < self.size]
            if len(tabu_list[p]) == 0:
                del tabu_list[p]
            else:
                tabu_list[p] = range(self.horizon)

        return tabu_list

    def search(self):
        self.tabu_list()
        new_routes = self.add_best_neighbors()

class VNS(Neighborhood):
    def __init__(self, horizon, collection):
        self.size = 50
        self.collection = collection
        self.horizon = horizon
        self.pickup_points = collection.waste_collection.pickup_points
        self._tabu_list = self.tabu_list()
        self.random_size = 500

    def tabu_list(self):
        return {}

    def random_neighbor(self, k):
        if k == 0:
            return self.random_add_point()
        elif k == 1:
            return self.random_change_point()
        elif k== 2:
            return self.random_remove()
        else:
            raise Exception('Invalid k', k)

    def neighborhood_change(self, current_collection, new_collection, k):
        if new_collection.waste_collected() > current_collection.waste_collected():
            return {'new_route': new_collection, 'k': 0}
        else:
            return {'new_route': current_collection, 'k': k + 1}

    def neighborhood(self, current_collection, k):
        if k == 0:
            return self.add_best_neighbors(current_collection)
        elif k == 1:
            return self.change_best_neighbors(current_collection)
        elif k== 2:
            return self.remove_best_neighbors(current_collection)
        else:
            raise Exception('Invalid k', k)


    def VND(self, current_collection, k_max):
        k = 0
        while k < k_max:
            new_collection = n.neighborhood(current_collection, k)
            w = [r.waste_collected() for r in new_collection]
            if len(w) == 0:
                k += 1
                continue
            w = max(w)
            new_collection = [r for r in new_collection if r.waste_collected() == w]
            t = [sum(r.time_h()) for r in new_collection]
            new_collection = [r for r in new_collection if sum(r.time_h()) == min(t)]
            new_collection = random.choice(new_collection)
            neigh_change = n.neighborhood_change(current_collection, new_collection, k)
            current_collection = neigh_change['new_route']
            k = neigh_change['k']
            print(current_collection.routes())
            print('Mierda recogida', current_collection.waste_collected())
            print(current_collection.time_h())
            print([len(r) for r in current_collection.routes()])

        return current_collection


    def GVNS(self, l_max, k_max, t_max):
        t = 0
        while t < t_max:
            k = 0
            while k < k_max:
                x = n.random_neighbor(k)
                x2 = n.VND(x, k_max=l_max)
                neigh_change = self.neighborhood_change(x, x2, k)
                if self.collection.time_constraint(neigh_change['new_route']) :
                    self.collection = neigh_change['new_route']
                k = neigh_change['k']
                print(self.collection.waste_collected())
            t += 1
        return t



waste_collection = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                    file_times="data/times-between-pickup-points.txt")

collection = RouteCollection(waste_collection,
                             orig=5,
                             dest=5,
                             horizon=7
                             )

s = TabuSearch(7, collection=collection)
n = VNS(7, collection=collection)

n.GVNS(3,3,100)


h = 0

routes = []
routes_time = []
for h, r in enumerate(n.collection.routes()):
    route2 = [r[0]]

    i = 1
    points = r[1:-1]
    while len(points) > 0:
        best_point = points[0]
        w = waste_collection.time_points(route2[-1], best_point)
        for p in points:
            if waste_collection.time_points(route2[-1], p) < w:
                best_point = p
                w = waste_collection.time_points(route2[-1], p)
        route2.append(best_point)
        points.remove(best_point)

    route2.append(r[-1])

    route_time = 0
    for i in range(len(route2) - 1):
        route_time += waste_collection.time_points(route2[i], route2[i+1])
    routes_time.append(route_time)

print(routes_time)

for i in range(10):
    print('Iteración', i)
    route_old = s.collection.routes()
    print('Add')
    nuevo = s.add_best_neighbors()
    if len(nuevo) == 0:
        print('Change')
        try:
            nuevo = s.change_best_neighbors()
        except:
            0
    if len(nuevo) == 0:
        print('remove best')
        try:
            nuevo = s.remove_best_neighbors()
        except:
            0

    if len(nuevo) == 0:

        print('random remove')
        nuevo = [s.random_remove()]

    t = [sum(r.time_h()) for r in nuevo]
    nuevo = [r for r in nuevo if sum(r.time_h()) == min(t)]
    nuevo = random.choice(nuevo)
    #if nuevo.waste_collected() >= s.collection.waste_collected():
    s.collection = nuevo
    route_new = s.collection.routes()
    s.update_tabu_list(route_old, route_new)

    print(s.tabu_list())
    print('Mierda recogida', s.collection.waste_collected())
    print(s.collection.time_h())
    print([len(r) for r in s.collection.routes()])
    print()
    #else:
    #    print('No mejora')
    #    s.update_tabu_list(route_old, route_old)

s.collection = s.random_remove()



s.add_best_neighbors()



sum([i*7 for i in waste_collection.fill_rate.values()])

random_neighbor = [s.random_add_point, s.random_change_point, s.random_remove]

max_iter = 100
k_max = 3
while i < max_iter:
    k = 0
    while k < k_max:
        random_route = random_neighbor[k]()
        new_route = TabuSearch(7, random_route)
        new_route.add_best_neighbors()





for i in range(7):    old = a.collection.routes()
    a.collection = random.choice(a.add_best_neighbors())
    new = a.collection.routes()
    s.update_tabu_list(old, new)
    print(s._tabu_list)

s.tabu_list()
prev_route = [[5,5],[5,5]]
new_route = [[5,5],[5,2045,5]]


points = collection.waste_collection.pickup_points.copy()
points.remove(2045)
points.remove(2055)

h = set(range(a.collection.horizon))
h2 = [h2 for h2, r in enumerate(a.collection.routes()) if len(r) > 2]
h = h.intersection(set(a.h_available()))
h = list(h)

points

a = Neighborhood(collection, [0, 3, 6], [])
a.collection = a.add_best_neighbors()[0]
a.collection.point_h_available(2045)
a.change_best_neighbors()
a.collection.routes()[0]

w = a.best_add()

a.h_available()

a.collection.add_point_waste_collected(2045, 1)

a.collection.add_point_waste_collected(2045)
a.waste_add()
a.add_best_neighbors()

a.random_add_point().routes()
a.random_change_point().routes()

class NeighborhoodAdd:
    def __init__(self, collection, h_tabu, points_tabu):
        self.collection = collection
        self.max_time = max_time
        self.h_tabu = h_tabu
        self.points_tabu = points_tabu





    def waste_point(self, point, h):
        w = {}
        h_orig = self.collection.h_with_point(point)
        h_available = self.collection.h_without_point(point)
        h_available = [h2 for h2 in h_available if h2 in h]
        h_available = self.h_point_constraint_time(h_available, point)
        for h_new in h_available:
            h_aux = h_orig + [h_new]
            h_aux.sort()
            w[h_new] = self.waste_point_h(point, h_aux)
        return w

    def waste_h(self, h, points):
        w = {}
        points = [p for p in self.collection.waste_collection.pickup_points if p in points]
        for p in points:
            w[p] = self.waste_point(p, h)

        point = []
        for p, h in w.items():
            point += [p] * len(h.values())

        h2 = []
        w2 = []
        for p, h in w.items():
            h2 += h.keys()
            w2 += h.values()

        d = {'point': point, 'h': h2, 'w': w2}
        w = pd.DataFrame(d)
        w.sort_values(by=['w'], inplace=True, ascending=False)
        return w

    def generate_neighbors(self, h, points):
        if h is None:
            h = range(7)
        waste = self.waste_h(h, points)
        new_routes = []
        b = 0
        for value in waste['w'].unique():
            waste2 = waste[waste['w'] == value]
            for i in range(len(waste2)):
                b += 1
                point = waste2.iloc[i, 0]
                h = waste2.iloc[i, 1]
                route = self.collection.extract_routes()[h]

                for pos in range(len(route) - 1):
                    new_route = self.collection.copy()

                    new_route.add_point(point, h, pos)

                    new_routes.append(new_route)
                new_routes = self.collection.filter_routes_time_constraint(new_routes)
            if len(new_routes) > 0:
                break
        return new_routes


collection = RouteCollection(waste_collection,
                             orig=5,
                             dest=5,
                             horizon=7
                             )

collection.h_add_point_max_time(2045)

neigh = NeighborhoodAdd(collection=collection)

a = neigh.random_neighbor()

a.routes()

collection
collection.new_collection()
class Neighborhood:
    def __init__(self, collection):
        self.collection = collection
        self.add = NeighborhoodAdd(collection)
