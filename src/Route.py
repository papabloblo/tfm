from src.sucio import waste_collection
from itertools import chain
import random as random
import time
import numpy as np
import copy
import multiprocessing as mp

class Route(waste_collection):
    def __init__(self, file_filling_rates, file_times):
        super().__init__(file_filling_rates, file_times)

    def route_time(self, route_seq):
        total_time = 0
        for i in range(len(route_seq)-1):
            total_time += self.time(route_seq[i], route_seq[i+1])
        return total_time

    def points_days_collection(self, route_seq):
        points = dict.fromkeys(chain(*route_seq), [])
        for h, r in enumerate(route_seq):
            for p in r:
                points[p] = points[p] + [h]
        return points

    def route_fill_level(self, route_seq):
        collected = [0] * len(route_seq)
        for p, r in self.points_days_collection(route_seq).items():
            for i, h in enumerate(r):
                if i == 0:
                    collected[h] += self.fill_level(point=p, days=h, fill_ini=True)
                else:
                    collected[h] += self.fill_level(point=p, days=r[i]-r[i-1], fill_ini=False)
        return collected

    def generate_routes(self, route_seq):
        route = []
        for r in route_seq:
            route.append(
                dict(
                    route=r,
                    time=self.route_time(r)
                )
            )
        fill_level = self.route_fill_level(route_seq)
        for h, fill in enumerate(fill_level):
            route[h]['fill_level'] = fill

        return route

    def generate_routes2(self, route_seq):
        route = []
        for r in route_seq:
            route.append(
                dict(
                    route=r,
                    time=self.route_time(r)
                )
            )

        return route

    def total_time(self, route=None):
        if route is None:
            route = self.route
        t = 0
        for i in route:
            t += i['time']
        return t

    def total_collect(self, route=None):
        if route is None:
            route = self.route
        t = 0
        for i in route:
            t += i['fill_level']
        return t

    def extract_routes(self, route):
        return [r['route'].copy() for r in route]




class Solution(Route):
    def __init__(self, orig, dest, horizon, file_filling_rates, file_times):
        super().__init__(file_filling_rates, file_times)
        self.orig = orig
        self.horizon = horizon
        self.dest = dest
        self.route = self.route_empty()
        self.max_time = 6.5*60*60

    def random_route(self, k=50):
        while True:
            routes = []
            try:
                for _ in range(self.horizon):
                    routes.append([self.orig] + random.sample(self.pickup_points, k=k) + [self.dest])
                routes = self.generate_routes(routes)
                break
            except:
                0
        return routes


    def route_empty(self):
        routes = []
        for _ in range(self.horizon):
            routes.append([self.orig, self.dest])
        return self.generate_routes(routes)

    def route_time2(self, route_orig, h, route_new, position):
        route_new = route_new[h]['route']
        route_base = route_orig[h]['route']
        base_time = route_orig[h]['time']

        base_time -= self.time(route_base[position - 1], route_base[position])
        base_time += self.time(route_new[position - 1], route_new[position])
        base_time += self.time(route_new[position], route_new[position + 1])

        return base_time

    def route_time3(self, route_orig, h, route_new, position):
        route_new = route_new[h]['route']
        route_base = route_orig[h]['route']
        base_time = route_orig[h]['time']

        base_time -= self.time(route_base[position - 1], route_base[position])
        base_time -= self.time(route_base[position], route_base[position + 1])
        base_time += self.time(route_new[position - 1], route_new[position])
        base_time += self.time(route_new[position], route_new[position + 1])

        return base_time

    def add_point(self, h, point, position):

        routes = self.extract_routes(self.route)

        new_route = copy.deepcopy(self.route)
        routes[h] = list(routes[h][0:position]) + [point] + list(routes[h][position:])
        new_route[h]['route'] = routes[h]

        new_route[h]['time'] = self.route_time2(route_orig=self.route, h=h, route_new=new_route, position=position)

        return new_route

    def swap_point(self, h, point, position):
        routes = self.extract_routes(self.route)

        new_route = copy.deepcopy(self.route)
        routes[h][position] = point
        new_route[h]['route'] = routes[h]
        new_route[h]['time'] = self.route_time3(self.route, h, new_route, position)

        return new_route

    def all_index(self):
        indexes = []
        for r in self.route:
            indexes.append(list(range(1, len(r['route']))))
        return indexes

    def all_points(self):
        points = []
        for r in self.route:
            points.append([i for i in self.pickup_points if i not in r['route']])
        return points

    def neighboorhood(self, points=None, indexes=None, n_points=10, n_indexes=5, h=None):

        if indexes is None:
            indexes = self.all_index()

        if points is None:
            points = self.all_points()
        if h is None:
            h2 = range(0, len(self.route))
        else:
            h2 = h
        routes = []
        for h in h2:
            fill = {}
            for p in points[h]:
                a = self.extract_routes(self.route)
                a[h] += [p]
                fill[p] = sum(self.route_fill_level(a))
            prob = [p/sum(fill.values()) for p in fill.values()]
            points2 = np.random.choice(points[h], size=min(n_points, len(points[h])), p=prob, replace=False)
            for p in list(points2):
                for i in np.random.choice(indexes[h], size=min(n_indexes, len(indexes[h])), replace=False):
                    try:
                        y = self.add_point(h, p, i)
                        for id, ab in enumerate(y):
                            if id == h:
                                y[id]['fill_level'] = fill[p]
                            else:
                                y[id]['fill_level'] = self.route[id]['fill_level']
                        routes.append(y)
                    except:
                        0
                if len(self.route[h]['route']) > 2:
                    try:
                        y = self.swap_point(h, p, i)
                        for id, ab in enumerate(y):
                            if id == h:
                                y[id]['fill_level'] = fill[p]
                            else:
                                y[id]['fill_level'] = self.route[id]['fill_level']
                        routes.append(y)
                    except:
                        0
        print("Se han creado", len(routes), "vecinos en", time.time() - start)
        return routes
        #return sorted(routes, key=lambda i: i['fill_level'], reverse=True)


    def neighboorhood2(self, points=None, indexes=None, n_points=10, n_indexes=5, h=None):
        start = time.time()
        if indexes is None:
            indexes = self.all_index()

        if points is None:
            points = self.all_points()
        if h is None:
            h2 = range(0, len(self.route))
        else:
            h2 = h
        routes = []
        for h in h2:
            fill = {}
            for p in points[h]:
                a = self.extract_routes(self.route)
                a[h] += [p]
                fill[p] = sum(self.route_fill_level(a))



            fill2 = list(set(fill.values()))
            fill2.sort()

            seguir = True
            while seguir and len(fill2) > 0:
                f = fill2.pop()
                points2 = [p for p, i in fill.items() if i == f]
                for p in list(points2):
                    for i in np.random.choice(indexes[h], size=min(n_indexes, len(indexes[h])), replace=False):
                        try:
                            y = self.add_point(h, p, i)
                            for id, ab in enumerate(y):
                                if id == h:
                                    y[id]['fill_level'] = fill[p]
                                else:
                                    y[id]['fill_level'] = self.route[id]['fill_level']
                            routes.append(y)
                        except:
                            0
                    if len(self.route[h]['route']) > 2:
                        try:
                            y = self.swap_point(h, p, i)
                            for id, ab in enumerate(y):
                                if id == h:
                                    y[id]['fill_level'] = fill[p]
                                else:
                                    y[id]['fill_level'] = self.route[id]['fill_level']
                            routes.append(y)
                        except:
                            0
                routes = self.route_time_constrain(routes)
                if len(routes) > 0:
                    seguir = False

        return routes
        #return sorted(routes, key=lambda i: i['fill_level'], reverse=True)

    def neighboorhood_par(self, points=None, indexes=None):

        start = time.time()
        if indexes is None:
            indexes = []
            for r in self.route:
                indexes.append(list(range(1, len(r['route']))))

        if points is None:
            points = []
            for r in self.route:
                points.append([i for i in self.pickup_points if i not in r['route']])
        pool = mp.Pool(processes=10)



        routes = [pool.apply(self.neigh_aux, args = (h, points[h], indexes[h])) for h in range(len(self.route))]

        pool.close()
                # if len(r['route']) > 2:
                #     try:
                #         routes.append(self.swap_point(h, p, i))
                #     except:
                #         0
        print("Se han creado", len(routes), "vecinos en", time.time() - start)
        return routes

    def neigh_aux(self, h, pi, ind):
        # h = 0
        fill = {}
        routes=[]
        for p in pi:
            a = self.extract_routes(self.route)
            a[h] += [p]
            fill[p] = sum(self.route_fill_level(a))
        prob = [p / sum(fill.values()) for p in fill.values()]
        points2 = np.random.choice(pi, size=min(50, len(points2)), p=prob, replace=False)
        for p in list(points2):
            for i in np.random.choice(ind, size=min(10, len(ind)), replace=False):
                try:
                    y = self.add_point(h, p, i)
                    for id, ab in enumerate(y):
                        if id == h:
                            y[id]['fill_level'] = fill[p]
                        else:
                            y[id]['fill_level'] = self.route[id]['fill_level']
                    routes.append(y)
                except:
                    0
                if len(selfroute[h]['route']) > 2:
                    try:
                        y = self.swap_point(h, p, i)
                        for id, ab in enumerate(y):
                            if id == h:
                                y[id]['fill_level'] = fill[p]
                            else:
                                y[id]['fill_level'] = self.route[id]['fill_level']
                        routes.append(y)
                    except:
                        0

        return routes

    def neighbor_fill(self, routes):
        return [self.total_collect(r) for r in routes]

    def time_constraint(self, route):
        ok = True
        for r in route:
            if r['time'] > self.max_time:
                ok = False
                break
        return ok

    def route_time_constrain(self, routes):
        return [r for r in routes if self.time_constraint(r) is True]

    def best_neighbor(self, routes, k=None):
        routes = self.route_time_constrain(routes)
        f = self.neighbor_fill(routes)

        neigh = [r for i, r in enumerate(routes) if f[i] == max(f)]
        if len(neigh) > 0:
            if k is None:
                k = len(neigh)
            prob = [1/self.total_time(r) for r in neigh]
            neigh = random.choices(neigh, k=1, weights=prob)
        else:
            neigh = [self.route]
            print("No hay vecino bueno")
        return neigh





#
# #mi.route = au[0]
# for i in range(10):
#     print("Iteración", i)
#     #point_random = [random.sample(mi.pickup_points, k=50) for _ in range(7)]
#     #index_random = [[random.choice(range(len(mi.route[i]['route'])))] for i in range(7)]
#     #index_random = [random.sample(range(1,len(r['route'])), k=2) for r in mi.route]
#     #ay = mi.neighboorhood(points=point_random, indexes=index_random)
#     ay = mi.neighboorhood(n_indexes=10, n_points=10)
#     #ay = mi.neighboorhood_par(points=point_random)
#     au = mi.best_neighbor(ay, k=1)
#     #print(au[0])
#     mi.route = au[0]
#     print("Tiempo medio:", mi.total_time()/7)
#     print("Recogida total:", mi.total_collect())
#     print("Puntos de recogida", [len(r['route']) for r in mi.route])
#     print("\n")


class TabuSearch:
    def __init__(self):
        self.tabu_h = dict.fromkeys(range(7), 0)

        self.max_tabu = 10
        self.max_tabu_h = 2
        self.iter = 0
        self.trace = {}

    def solution(self, sol):
        self.Solution = sol
        self.tabu_points = dict.fromkeys(self.Solution.pickup_points, 0)

    def update_candidates_old(self, route_new):
        route_new = tabu.Solution.extract_routes(route_new)
        orig = tabu.Solution.extract_routes(tabu.Solution.route)

        tabu.tabu_points = {p: i+1 for p, i in tabu.tabu_points.items() if i < tabu.max_tabu}

        for h in range(len(route_new)):
            if route_new[h] != orig[h]:
                p = [p for p in route_new[h] if p not in orig[h]][0]
                if p in tabu.tabu_points.keys():
                    tabu.tabu_points[p] += 1
                else:
                    tabu.tabu_points[p] = 1


    def update_candidates(self, route_new):
        points = tabu.Solution.extract_routes(tabu.Solution.route)
        points = list(chain(*points, []))
        points = [p for p in points if p not in [tabu.Solution.orig, tabu.Solution.dest]]
        tabu_points = dict.fromkeys(tabu.Solution.pickup_points, 0)
        for p in points:
            tabu_points[p] += 1
        self.tabu_points = tabu_points

    def update_h_old(self, route_new):
        route_new = tabu.Solution.extract_routes(route_new)
        orig = tabu.Solution.extract_routes(tabu.Solution.route)

        #tabu.tabu_h = {p: i+1 for p, i in tabu.tabu_h.items() if i < tabu.max_tabu_h}

        for h in range(len(route_new)):
            if route_new[h] != orig[h]:
                if h in tabu.tabu_h.keys():
                    tabu.tabu_h[h] += 1
                else:
                    tabu.tabu_h[h] = 1

    def update_h(self, route_new):
        self.tabu_h = {h: len(r['route']) for h, r in enumerate(route_new)}

    def update_trace(self, n_points, n_indexes):
        self.trace[self.iter] = {"n_points": n_points,
                            "n_indexes": n_indexes,
                            "tabu_h": self.max_tabu_h,
                            "tabu_points": self.max_tabu,
                            "error": self.Solution.total_collect(),
                            "solution": self.Solution.route}

    def h_available(self):
        tabu2 = tabu.tabu_h.values()
        tabu2 = list(set(tabu2))
        tabu2.sort()
        tabu2 = tabu2[:tabu.max_tabu_h]
        tabu3 = {p: i for p, i in tabu.tabu_h.items() if i in tabu2}
        return list(tabu3.keys())
        #return [h for h in range(7) if h in tabu3.]

    def candidates_available(self):
        tabu2 = tabu.tabu_points.values()
        tabu2 = list(set(tabu2))
        tabu2.sort()
        tabu2 = tabu2[:tabu.max_tabu]
        tabu3 = {p: i for p, i in tabu.tabu_points.items() if i in tabu2}
        tabu3 = [list(tabu3.keys())]*len(tabu.tabu_h)
        return tabu3

    def candidates_available_old(self):
        points = self.Solution.all_points()
        for h in range(len(points)):
            points[h] = [p for p in points[h] if p not in self.tabu_points.keys()]
        return points

    def optimize(self, n_iter=10, n_indexes=10, n_points=10, indexes=None, print_each=10):
        max_iter = self.iter + n_iter
        for i in range(n_iter):
            self.iter += 1

            start = time.time()
            neighbors = tabu.Solution.neighboorhood2(points=tabu.candidates_available(),
                                                    n_indexes=n_indexes,
                                                    n_points=n_points,
                                                    indexes=indexes,
                                                    h=tabu.h_available()
                                                    #n_points = i
                                                    )
            new_sol = tabu.Solution.best_neighbor(neighbors, k=1)[0]
            tabu.update_candidates(route_new = new_sol)
            tabu.update_h(route_new=new_sol)
            tabu.Solution.route = new_sol
            self.update_trace(n_points, n_indexes)
            if i%print_each == 0:
                print("Iteración", self.iter, "de", max_iter)
                print(self.tabu_points)
                print(self.tabu_h)
                print("Se han creado", len(neighbors), "vecinos en", time.time() - start)
                print("Tiempo medio:", round(self.Solution.total_time()/len(self.Solution.route),2))
                print("Recogida total:", round(self.Solution.total_collect(), 2))
                print("Puntos de recogida", [len(r['route']) for r in self.Solution.route])
                print('Número medio de visitas', round(sum(tabu.tabu_points.values())/len(tabu.tabu_points.values()),2))
                print("\n")

mi = Solution(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
              file_times="data/times-between-pickup-points.txt",
              orig= 5,
              dest = 5,
              horizon = 7)


tabu = TabuSearch()
tabu.solution(mi)
tabu.max_tabu = 5
tabu.max_tabu_h = 2
tabu.optimize(5, n_points=1000, n_indexes=200, indexes=None, print_each=1)



tabu.Solution.route_time(route)

route2 = route.copy()

mi.time(5, 6643)

for h in range(len(mi.route)):
    route = tabu.Solution.extract_routes(tabu.Solution.route)[h]
    route2 = route.copy()
    for a in range(len(route2)-1):
        dist = []
        for i in range(a+1, len(route2)):
            dist.append(mi.time(route2[a], route2[i]))

        mejor = [i for i, d in enumerate(dist) if d == min(dist)][0] + a + 1

        route3 = route2[:a+1] + [route2[mejor]] + route2[a+1:mejor] + route2[mejor+1:]

        #if mi.route_time(route3) < mi.route_time(route2):
        route2 = route3
        print(mi.route_time(route2))

    mi.route[h]['route'] = route2
    mi.route[h]['time'] = mi.route_time(route2)

mi.route[0]['time']
mi.route_time(mi.route[0]['route'])

for k in range(7):
    tabu.optimize(10, n_points=25, n_indexes=40, indexes=None, h=[5])


aux = au[0]
aux = mi.extract_routes(aux)
orig = mi.extract_routes(mi.route)

tabu_points = {}
for h in range(len(aux)):
    if aux[h] != orig[h]:
        p = [p for p in aux[h] if p not in orig[h]][0]
        if p in tabu_points.keys():
            tabu_points[p] += 1
        else:
            tabu_points[p] = 1







mi.route = mi.random_route(k=3)
mi.add_point(h=1, point=2053, position=1)



def miau(h,points, indexes):
    a = []
    for p in points[h]:
        for i in indexes[h]:
            try:
                a += mi.add_point(h=h, point=p, position=i)
            except:
                0
    return a

pool = mp.Pool(mp.cpu_count()-1)
point = random.sample(mi.pickup_points, k=200)
result = [pool.apply(miau, args=(1, p, 1)) for p in point]
pool.close()


cProfile.run('mi.neighboorhood(points=point_random, indexes=index_random)')

len(mi.time_constraint(ay))
len(ay)
mi.add_point(1, 2045, 0)
mi.swap_point(1, 2045, 1)
mi.route
route_seq = [[2045, 2046, 2047], [2045, 2055, 2053]]
mi.generate_routes()
mi.points_days_collection(route_seq)
mi.days_since_collect(route_seq)
mi.generate_routes(route_seq)
mi.route
mi.total_time()
mi.total_collect()