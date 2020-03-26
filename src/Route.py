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
        self.max_time=6*60*60

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

    def add_point(self, h, point, position):

        routes = mi.extract_routes(mi.route)
        routes[h] = list(routes[h][0:position]) + [point] + list(routes[h][position:])

        base_time = mi.route[h]['time']

        base_time -= mi.time(mi.route[h]['route'][position - 1], mi.route[h]['route'][position])
        base_time += mi.time(routes[h][position - 1], routes[h][position])
        base_time += mi.time(routes[h][position], routes[h][position + 1])
        new_route = copy.deepcopy(mi.route)
        new_route[h]['route'] = routes[h]
        new_route[h]['time'] = base_time
        return new_route

    def swap_point(self, h, point, position):
        routes = self.extract_routes(self.route)
        routes[h][position] = point

        base_time = mi.route[h]['time']

        base_time -= mi.time(mi.route[h]['route'][position - 1], mi.route[h]['route'][position])
        base_time += mi.time(routes[h][position - 1], routes[h][position])
        base_time += mi.time(routes[h][position], routes[h][position + 1])
        new_route = copy.deepcopy(mi.route)
        new_route[h]['route'] = routes[h]
        new_route[h]['time'] = base_time

        return new_route

    def neighboorhood(self, points=None, indexes=None):
        start = time.time()
        if indexes is None:
            indexes = []
            for r in self.route:
                indexes.append(list(range(1, len(r['route']))))

        if points is None:
            points = []
            for r in self.route:
                points.append([i for i in self.pickup_points if i not in r['route']])


        routes = []
        iter = 0
        for h, r in enumerate(self.route):
            #h = 0
            fill = {}
            for p in points[h]:
                a = self.extract_routes(mi.route)
                a[h] += [p]
                fill[p] = sum(self.route_fill_level(a))
            prob = [p/sum(fill.values()) for p in fill.values()]
            points2 = np.random.choice(points[h], size=100, p=prob, replace=False)
            for p in list(points2):
                for i in np.random.choice(indexes[h], size=min(10, len(indexes[h])), replace=False):
                    try:
                        y = self.add_point(h, p, i)
                        for id, ab  in enumerate(y):
                            if id == h:
                                y[id]['fill_level'] = fill[p]
                            else:
                                y[id]['fill_level'] = self.route[id]['fill_level']
                        routes.append(y)
                    except:
                        0
                if len(r['route']) > 2:
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

    def neighboorhood_par(self, points=None, indexes=None):

        start = time.time()
        if indexes is None:
            indexes = []
            for r in mi.route:
                indexes.append(list(range(1, len(r['route']))))

        if points is None:
            points = []
            for r in self.route:
                points.append([i for i in self.pickup_points if i not in r['route']])
        pool = mp.Pool(processes=7)



        routes = [pool.apply(self.neigh_aux, args = (h, points[h], indexes)) for h in range(len(self.route))]

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
            a = self.extract_routes(mi.route)
            a[h] += [p]
            fill[p] = sum(self.route_fill_level(a))
        prob = [p / sum(fill.values()) for p in fill.values()]
        points2 = np.random.choice(pi, size=50, p=prob, replace=False)
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
                if len(mi.route[h]['route']) > 2:
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



mi = Solution(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
              file_times="data/times-between-pickup-points.txt",
              orig= 5,
              dest = 5,
              horizon = 7)



mi.route = au[0]
for i in range(50):
    print("Iteración", i)
    #point_random = [random.sample(mi.pickup_points, k=50) for _ in range(7)]
    #index_random = [[random.choice(range(len(mi.route[i]['route'])))] for i in range(7)]
    #index_random = [random.sample(range(1,len(r['route'])), k=2) for r in mi.route]
    #ay = mi.neighboorhood(points=point_random, indexes=index_random)
    ay = mi.neighboorhood()
    #ay = mi.neighboorhood_par(points=point_random)
    au = mi.best_neighbor(ay, k=1)
    #print(au[0])
    mi.route = au[0]
    print("Tiempo medio:", mi.total_time()/7)
    print("Recogida total:", mi.total_collect())
    print("Puntos de recogida", [len(r['route']) for r in mi.route])
    print("\n")








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