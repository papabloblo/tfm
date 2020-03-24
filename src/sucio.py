import pandas as pd
import random as random
import math


class waste_collection:
    def __init__(self, file_filling_rates, file_times):
        self.fill_rate = self.read_filling_rates(file_filling_rates)
        self.times = self.read_times(file_times)
        self.pickup_points = list(self.fill_rate.keys())

    def read_filling_rates(self, file_filling_rates):
        fill_rate = pd.read_csv(file_filling_rates)

        tasa = fill_rate['TASA'].to_list()

        tasa_num = []
        for i in tasa:
            try:
                tasa_num.append(float(i))
            except:
                tasa_num.append(0)

        punto = fill_rate['PUNTO'].to_list()
        fill_rate = {point: rate for point, rate in zip(punto, tasa_num)}

        return fill_rate

    def read_times(self, file_times):
        times = pd.read_table(file_times)

        times = times.rename(columns={'# PickupPoint': 'origen', 'PickupPoint': 'destino', 'Time(s.)': 'tiempo'})
        return times

    def time(self, orig, dest):
        return self.times[(self.times['origen'] == orig) & (self.times['destino'] == dest)]["tiempo"].values[0]

    def fill_level(self, point, days):
        return min(1, self.fill_rate[point]*days)



class Route(waste_collection):
    def __init__(self, file_filling_rates, file_times, orig, dest, horizon=7):
        super().__init__(file_filling_rates, file_times)
        self.orig = orig
        self.dest = dest
        self.initial_route = self.new_route([self.orig, self.dest])
        self.route = self.initial_route.copy()
        self.last_collection = {}
        self.pick = self.collection_point()
        self.horizon = horizon


    def new_route(self, route_seq, h=None):

        return dict(route=route_seq,
                    time=self.route_time(route_seq),
                    collected=self.route_fill_level(route_seq)
                    )

    def new_route_day

    def new_route(self, route_seq):
        if h is None:
            h = range(self.horizon)
        elif type(h) is not list:
            h = [h]
            route_seq = [route_seq]

    def neighboorhood(self, route=None, candidates=None, indexes=None):
        if route is None:
            route = self.route.copy()
        if indexes is None:
            indexes = range(1, len(route)-1)
        if candidates is None:
            candidates = [i for i in self.pickup_points if i not in route['route']]

        routes = []
        for point in candidates:
            for i in indexes:
                try:
                    routes.append(self.new_point(point, i, route))
                except:
                    0
                if len(route['route']) > 2:
                    try:
                        routes.append(self.swap_point(point, i, route))
                    except:
                        0
        return sorted(routes, key=lambda i: i['collected'], reverse=True)

    def route_time(self, route):
        total_time = 0
        for i in range(len(route)-1):
            total_time += self.time(route[i], route[i+1])
        return total_time

    def swap_point(self, candidate, index, route=None):
        if route is None:
            route = self.route.copy()
        route2 = route['route'].copy()
        route2[index] = candidate
        return self.new_route(route2)

    def new_point(self, new_point, index, route=None):
        if route is None:
            route = self.route.copy()
        new_seq = list(route["route"][0:index]) + [new_point] + list(route["route"][index:])
        return self.new_route(new_seq)


    def route_fill_level(self, route_seq):
        return sum([self.fill_level(i, 1) for i in route_seq])

    def random_route(self, k=10, candidates=None):
        if candidates is None:
            candidates = [i for i in self.pickup_points if i not in self.initial_route['route']]

        return [self.orig] + (random.choices(candidates, k=k-2)) + [self.dest]

    def update_collection_days(self, candidate, h):
        self.last_collection[candidate]

    def collection_point(self):
        collection = {}
        for i in self.pickup_points:
            collection[i] = dict(fill_rate=self.fill_rate[i],
                                 days_since_collection=list(range(0, self.horizon))
                                 )
        return collection


last_collection = {158: [3,4,5,1,2]}

a = [5, 6, 7, 1, 2, 3]

a[2:] = range(1, len(a)-1)

collection_point = {1925: {'fill_rate': 0.3, 'days_since_collection': [3, 4, 5, 1, 2]}}

h = [2,4]


collection_point[1925]['days_since_collection'][0:h[0]] + list(range(1, h[1]-1))


class constraints:
    def __init__(self, max_time=6*60*60):
        self.max_time = max_time

    def route_max_time(self, route):
        return route["time"] <= self.max_time

    def constraint_satisfaction(self, routes):
        return [i for i in routes if self.route_max_time(i)]


mi = Route(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
           file_times="data/times-between-pickup-points.txt",
           orig = 7458,
           dest = 7391)

mi.fill_rate

class TabuSearch:
    def __init__(self, max_iter=10):
        self.tabu_candidates = {}
        self.tabu_indexes = {}
        self.max_iter = max_iter

    def new_candidate(self, candidate):
        self.tabu_candidates[candidate] = 0

    def new_index(self, index):
        self.tabu_indexes[index] = 0

    def drop_candidate(self, candidate):
        del self.tabu_candidates[candidate]

    def drop_index(self, index):
        del self.tabu_indexes[index]

    def update_iter(self):
        for i in self.tabu_candidates.keys():
            self.tabu_candidates[i] += 1
        for i in self.tabu_indexes.keys():
            self.tabu_indexes[i] += 1

    def drop_max_iter(self):
        for i in self.tabu_candidates.keys():
            if self.tabu_candidates[i] > self.max_iter:
                del self.tabu_candidates[i]

        for i in self.tabu_indexes.keys():
            if self.tabu_indexes[i] > self.max_iter:
                del self.tabu_indexes[i]

    def


guau = TabuSearch()
guau.new_candidate(12356)
guau.tabu_candidates
guau.update_iter()
guau.tabu_candidates
guau.drop_candidate(12356)
guau.tabu_candidates


mi.route = mi.new_route([7458,2239,7391])
mi.neighboorhood()
au = mi.neighboorhood(candidates=[2240, 2286])
au
ji = constraints()

ji.constraint_satisfaction(au)

mi.random_route(k=3)
mi.new_point(2070,1)
route = mi.route([7458, 8183, 7391])

route = random.choices(candidates,k=12)
mi.neighboorhood(candidates=[2239, 2240])

candidates = list(mi.fill_rate.keys())
candidates = [i for i in candidates if i not in route['route']]
miau = mi.neighboorhood(route, candidates)
len(mi.constraint_satisfaction(miau))
len(miau)
route = mi.route(route)
mi.time_constraint(route)

class route:
    def __init__(self):
        self.max_time = 6*60*60
    def time_constraint(self, route):






distancia_total = 0
for i, p in enumerate(route[1:]):
    distancia_total += mi.distancia(route[i], p)
    print(distancia_total)

route = [7458, 8183, 7391]




positions = range(0, len(route))

i = 0

generate_new_route

mi.route_time(new_route)
mi.route_time(route)


for p in enumerate(mi.fill_rate.keys())
neighborhood

mi.generate_new_route(route=route, index=9, new_point=0)
new_point=2586
route
index=2
list(route[:index+1]) + [new_point] + list(route[index + 1:])

route = random.choices(list(mi.fill_rate.keys()), k=4)

candidates = [i for i in candidates if i not in route]

candidate_list = {}
for point in candidates:
    print(point)
    current_time = mi.route_time(route)
    route2 = route
    best_time = math.inf
    for i in range(1, len(route)):
        t2 = current_time
        try:
            t2 -= mi.distancia(route[i-1], route[i])
            t2 += mi.distancia(route[i - 1], point)
            t2 += mi.distancia(point, route[i])
            if t2 < best_time:
                new_route = mi.generate_new_route(route, i, point)
                best_time = t2
        except:
            0
    if len(t) > 0:
        candidate_list[point] = {min(t): t[min(t)]}




min([candidate_list[i].values() for i in candidate_list])

r = mi.generate_new_route(route=route, index=i, new_point=point)

[mi.route_time(a) for a in r]

mi.distancia(route2[0], route2[1])

mi.times[mi.times["origen"] == route2[0]][mi.times["destino"] == route2[2]]

route2 = mi.generate_new_route(route=route, index=i, new_point=point)


candidates = list(mi.fill_rate.keys())

route = random.choices(list(mi.fill_rate.keys()), k=2)

si = mi.best_position(route, candidates)

mi.fill_level(candidates[0], 5)



mi.generate_new_route(route, 1, 7978)
mi.best_position(route, candidates)

fill = {i: mi.fill_level(i, 2) for i in candidates}

si = [i for i in fill.keys() if fill[i] == max(fill.values())]

mi.best_position(route, si)
route = mi.generate_new_route(route, 1, 2136)


origen = 0
destino = 5
route = [origen, destino]

for i in range(0, 100):
    candidates = [i for i in mi.pickup_points if i not in route]

    fill = [mi.fill_level(i, 2) for i in candidates]

    fill_rate_candidates = [candidate for i, candidate in enumerate(candidates) if fill[i] == max(fill)]
    mejor = mi.best_position(route, fill_rate_candidates)
    route = mejor["route"]

mi.route_time(route)
6*60*60