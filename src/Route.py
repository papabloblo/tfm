from itertools import chain
import pandas as pd
#~from Neighborhood2 import NeighborhoodAdd, NeighborhoodSwap, NeighborhoodChange
#from Tabu import Tabu

class Route:
    def __init__(self, waste_collection, orig, dest, route=None):
        self.waste = waste_collection
        self.orig = orig
        self.dest = dest

        if route is None:
            route = [self.orig, self.dest]

        self.__route = route
        self.__time = self.calculate_time()

    def calculate_time(self):
        route_time = 0
        for i in range(len(self.__route) - 1):
            route_time += self.waste.time_points(self.__route[i], self.__route[i+1])
        return route_time

    def update(self, new_route):
        if new_route[0] != self.orig and new_route[-1] != self.dest:
            raise Exception("No se pude modificar el origen o el destino")
        self.__route = new_route.copy()
        self.__time = self.calculate_time()

    def time(self):
        return self.__time

    def route(self):
        return self.__route

    def add_time(self, point, position):
        new_route = list(self.__route[0:position + 1]) + [point] + list(self.__route[position + 1:])

        time = self.__time

        time -= self.waste.time_points(self.__route[position], self.__route[position + 1])

        time += self.waste.time_points(new_route[position], new_route[position + 1])
        time += self.waste.time_points(new_route[position + 1], new_route[position + 2])

        return {'new_route': new_route, 'new_time': time}

    def add_point(self, point, position):
        if position >= len(self.__route)-1:
            raise Exception("No se puede añadir un punto después del destino")

        add = self.add_time(point, position)

        self.__route = add['new_route']
        self.__time = add['new_time']

    def change_time(self, point, position):
        new_route = self.__route.copy()
        new_route[position] = point

        time = self.__time

        time -= self.waste.time_points(self.__route[position - 1], self.__route[position])
        time -= self.waste.time_points(self.__route[position], self.__route[position + 1])

        time += self.waste.time_points(new_route[position - 1], new_route[position])
        time += self.waste.time_points(new_route[position], new_route[position + 1])

        return {'new_route': new_route, 'new_time': time}

    def change_point(self, point, position):
        if position == 0 or position == len(self.__route):
            raise Exception("No se pude modificar el destino o el origen")

        change = self.change_time(point, position)

        self.__route = change['new_route']
        self.__time = change['new_time']

    def remove_point(self, position):
        if position == 0 or position == len(self.__route):
            raise Exception("No se pude modificar el destino o el origen")

        new_route = self.__route.copy()
        del new_route[position]

        time = self.__time

        time -= self.waste.time_points(self.__route[position - 1], self.__route[position])
        time -= self.waste.time_points(self.__route[position], self.__route[position + 1])

        time += self.waste.time_points(new_route[position - 1], new_route[position])

        self.__route = new_route
        self.__time = time

    def available_points(self):
        return [p for p in self.waste.pickup_points if p not in self.__route]

    def available_add_positions(self):
        return list(range(len(self.__route)-1))



class RouteCollection(NeighborhoodAdd, NeighborhoodSwap, NeighborhoodChange):

    def __init__(self,
                 waste_collection,
                 orig,
                 dest,
                 horizon=6,
                 routes=None,
                 max_time=6.5*60*60,
                 waste_add=None,
                 time_add=None,
                 max_tabu=50):

        self.waste_collection = waste_collection
        self.horizon = horizon
        self.orig = orig
        self.dest = dest
        self.collection = self.create(routes)
        self.waste_collected_point = self.calculate_waste_collected_point()
        self.max_time = max_time
        self.tabu = Tabu(collection_points=self.waste_collection.pickup_points,
                         horizon=self.horizon,
                         route=self.routes(),
                         max_tabu=max_tabu)
        if waste_add is None:
            self.waste_add = pd.DataFrame({'point': [], 'h': [], 'waste': []})
            self.update_waste_add()
        else:
            self.waste_add = waste_add

        if time_add is None:
            self.time_add = pd.DataFrame({'point': [], 'h': [], 'pos': [], 'total_time': [], 'total_waste': []})
            self.time_add['point'] = self.time_add['point'].astype('int')
            self.time_add['h'] = self.time_add['h'].astype('int')
            self.time_add['pos'] = self.time_add['pos'].astype('int')
            self.update_time_add()
        else:
            self.time_add = time_add

        while self.time_add.empty and not self.waste_add.empty:
            self.waste_add = self.waste_add[self.waste_add['waste'] != max(self.waste_add['waste'])]
            self.update_time_add()

    def h(self):
        return list(range(self.horizon))

    def available_points(self, h):
        return self.collection[h].available_points()

    def available_add_positions(self, h):
        return self.collection[h].available_add_positions()

    def create(self, routes):

        if routes is None:
            routes = [None]*self.horizon

        collection = []
        for h in range(self.horizon):
            collection.append(
                Route(
                    self.waste_collection,
                    orig=self.orig,
                    dest=self.dest,
                    route=routes[h]
                )
            )

        return collection

    def routes(self):
        return [r.route() for r in self.collection]

    def copy(self):
        route = RouteCollection(waste_collection=self.waste_collection,
                               orig=self.orig,
                               dest=self.dest,
                               horizon=self.horizon,
                               routes=self.routes(),
                               waste_add=self.waste_add,
                               time_add=self.time_add
                               )
        route.tabu.tabu_list = self.tabu.tabu_list.copy()
        return route

    def add_point(self, point, h, position):
        self.collection[h].add_point(point, position)
        self.update_waste_collected_point()

    def change_point(self, point, h, position):
        self.collection[h].change_point(point, position)
        self.update_waste_collected_point()

    def remove_point(self, h, position):
        self.collection[h].remove_point(position)
        self.update_waste_collected_point()

    def swap_point(self, h1, h2, position1, position2):
        routes = self.routes()
        p1 = routes[h1][position1]
        p2 = routes[h2][position2]
        self.collection[h1].change_point(p2, position1)
        self.collection[h2].change_point(p1, position2)
        self.update_waste_collected_point()

    def update_route(self, h, new_route):
        self.collection[h].update(new_route)
        self.update_waste_collected_point()

    def unique_points(self):
        points = list(set(chain(*self.routes())))
        return [p for p in points if p in self.waste_collection.pickup_points]

    def time_h(self):
        return [r.time() for r in self.collection]

    def random_point_h(self, points=None, h=None):
        if points is None:
            points = self.waste_collection.pickup_points

        if h is None:
            h = range(self.horizon)

        h = random.choice(h)
        route_h = self.routes()[h]

        points = [p for p in points if p not in route_h]
        point = random.choice(points)

        return {'point': point, "h": h}

    def waste_collected_point_h(self, point, h):
        fill_ini = self.waste_collection.fill_ini[point]
        waste = 0
        for i in range(len(h)):
            if i == 0:
                d = h[i]
                waste += self.waste_collection.fill_level(point, d, fill_ini=fill_ini)
            else:
                d = h[i] - h[i - 1]
                waste += self.waste_collection.fill_level(point, d, fill_ini=0)
        return waste

    def waste_collected_point_h2(self, point, h):
        fill_ini = self.waste_collection.fill_ini[point]
        waste = {}
        for i in range(len(h)):
            if i == 0:
                d = h[i]
                waste[h[i]] = self.waste_collection.fill_level(point, d, fill_ini=fill_ini)
            else:
                d = h[i] - h[i - 1]
                waste[h[i]] = self.waste_collection.fill_level(point, d, fill_ini=0)
        return waste

    def mean_waste_h(self):
        w = [[] for h in range(self.horizon)]
        for p, h in self.point_h().items():
            w2 = self.waste_collected_point_h2(p, h)
            for h2, w3 in w2.items():
                w[h2].append(w3)

        return [sum(w3)/max(1, len(w3)) for w3 in w]

    def point_h2(self, point):
        return [h for h, r in enumerate(self.routes()) if point in r]

    def point_h(self):
        return {p: self.point_h2(p) for p in self.unique_points()}

    def calculate_waste_collected_point(self):
        return {p: self.waste_collected_point_h(p, self.point_h2(p)) for p in self.unique_points()}

    def update_waste_collected_point(self):
        self.waste_collected_point = self.calculate_waste_collected_point()

    def diff_waste_collected(self):
        w = {p: self.waste_collection.real_fill_level(p, max(h)) - self.waste_collected_point[p] for p, h in self.point_h().items()}
        return sum(w.values())

    def waste_collected(self, waste_collected=None):
        if waste_collected is None:
            waste_collected = self.waste_collected_point

        return sum(waste_collected.values())

    def add_point_h_waste_collected(self, point, h):

        waste_collected = self.waste_collected_point.copy()

        h_orig = self.point_h2(point)
        if h not in h_orig:
            h = h_orig + [h]
        else:
            h = [h]
        h.sort()

        waste_collected[point] = self.waste_collected_point_h(point, h)

        #return self.waste_collected(waste_collected)
        if point in self.waste_collected_point:
            w = waste_collected[point] - self.waste_collected_point[point]
        else:
            w = waste_collected[point]
        return w

    def add_point_waste_collected(self, point, h=None):
        if h is None:
            h = self.point_h_available(point)
        return {h2: self.add_point_h_waste_collected(point, h2) for h2 in h}

    def h_without_point(self, point):
        return [h for h, r in enumerate(self.routes()) if point not in r]

    def h_with_point(self, point):
        routes = self.routes()
        return [h for h, r in enumerate(routes) if point in r]

    def h_add_point_max_time(self, point):
        h = range(self.horizon)
        routes = self.routes()
        h_new = []
        for h2 in h:
            current_time = self.time_h()[h2]
            min_new_time = self.waste_collection.min_time_point(point, routes[h2])
            if current_time + min_new_time <= self.max_time:
                h_new.append(h2)
        return h_new

    def point_h_available(self, point):
        h = set(self.h_without_point(point))
        if max(self.time_h()) <= self.max_time:
            h_constraint_time = set(self.h_add_point_max_time(point))

            h = list(h.intersection(h_constraint_time))
        else:
            h = [h2 for h2 in h if self.time_h()[h2] <= self.max_time]
        h.sort()

        return h

    def time_constraint(self):
        return max(self.time_h()) <= self.max_time

    def total_time(self):
        return sum(self.time_h())

    def points_h_available(self):
        """

        :param new_collection:
        :return: dictionary with points and h available
        """

        pickup_points = self.waste_collection.pickup_points
        h_p = {}
        for p in pickup_points:
            h_p[p] = self.h_without_point(p)
            h_p[p] = list(set(h_p[p]).difference(set(self.tabu.tabu_p(p))))
        return h_p

    def update_waste_add(self, point=None):

        points_h_available = self.points_h_available()

        if point is not None:
            self.waste_add = self.waste_add[self.waste_add['point'] != point]
            points_h_available = {point: points_h_available[point]}
        else:
            self.waste_add = pd.DataFrame({'point': [], 'h': [], 'waste': []})

        waste = {'point': [], 'h': [], 'waste': []}
        for p, h in points_h_available.items():
            #total_waste = self.waste_collected()
            #total_waste -= self.waste_collected_point_h(p, self.h_with_point(p))
            for h_aux in h:
                waste['point'].append(p)
                waste['h'].append(h_aux)
                new_h = self.h_with_point(p)
                new_h.append(h_aux)
                new_h.sort()

                #waste['waste'].append(total_waste + self.waste_collected_point_h(p, new_h))
                waste['waste'].append(self.waste_collected_point_h(p, new_h) - self.waste_collected_point_h(p, self.h_with_point(p)))

        waste = pd.DataFrame(waste)

        waste['point'] = waste['point'].astype('int')
        waste['h'] = waste['h'].astype('int')

        if self.waste_add.empty:
            self.waste_add = waste
        else:
            self.waste_add = self.waste_add.append(waste)

        self.waste_add = self.waste_add[self.waste_add['waste'] > 0.001]
        self.waste_add.sort_values(by=['waste'], inplace=True, ascending=False)
        self.waste_add = self.waste_add.reset_index(drop=True)

    def update_time_add(self, h=None):

        self.time_add = self.time_add.drop(columns=['total_waste'])
        self.time_add = self.time_add[self.time_add['h'] != h]
        best_w = self.waste_add['waste'].max()
        waste_aux = self.waste_add[self.waste_add['waste'] == best_w]

        if h is not None:
            waste_aux = waste_aux[waste_aux['h'] == h]
            self.time_add = self.time_add[self.time_add['h'] != h]
        else:
            self.time_add = pd.DataFrame({'point': [], 'h': [], 'pos': [], 'total_time': []})
            self.time_add['point'] = self.time_add['point'].astype('int')
            self.time_add['h'] = self.time_add['h'].astype('int')
            self.time_add['pos'] = self.time_add['pos'].astype('int')

        aux = {'point': [], 'h': [], 'pos': [], 'total_time': []}

        for i in waste_aux.index:
            point_aux = waste_aux['point'][i]
            h_aux = waste_aux['h'][i]
            for pos in self.available_add_positions(h_aux):

                if self.time_add[(self.time_add['point'] == point_aux) & (self.time_add['h'] == h_aux) & (self.time_add['pos'] == pos)].empty:

                    new_time = self.collection[h_aux].add_time(point_aux, pos)
                    aux['point'].append(point_aux)
                    aux['h'].append(h_aux)
                    aux['pos'].append(pos)
                    max_time = self.time_h().copy()
                    max_time[h_aux] = new_time['new_time']
                    aux['total_time'].append(max(max_time))


        aux = pd.DataFrame(aux)

        aux['point'] = aux['point'].astype('int')
        aux['h'] = aux['h'].astype('int')
        aux['pos'] = aux['pos'].astype('int')

        self.time_add = self.time_add.append(aux)
        self.time_add = self.time_add[self.time_add['total_time'] <= self.max_time]

        self.time_add['total_waste'] = best_w

        self.time_add.sort_values(by=['total_time'], inplace=True)
        self.time_add = self.time_add.reset_index(drop=True)

    def calculate_waste_swap(self):

        points = self.unique_points()
        aux = {'p1': [], 'p2': [], 'h1': [], 'h2': [], 'total_waste': [], 'total_time': [], 'max_time': []}
        for p1 in points:
            h_with_p1 = self.h_with_point(p1)
            h_without_p1 = self.h_without_point(p1)
            for h1 in h_with_p1:
                for h2 in h_without_p1[h1:]:
                    for p2 in self.routes()[h2][1:-1]:
                        if p2 in self.routes()[h1]:
                            continue

                        total_waste = self.waste_collected()

                        total_waste -= self.waste_collected_point_h(p1, self.h_with_point(p1))
                        total_waste -= self.waste_collected_point_h(p2, self.h_with_point(p2))

                        new_h_p1 = [h for h in h_with_p1 if h != h1]
                        new_h_p1.append(h2)
                        new_h_p1.sort()

                        new_h_p2 = [h for h in self.h_with_point(p2) if h != h2]
                        new_h_p2.append(h1)
                        new_h_p2.sort()

                        total_waste += self.waste_collected_point_h(p1, new_h_p1)
                        total_waste += self.waste_collected_point_h(p2, new_h_p2)

                        aux['p1'].append(p1)
                        aux['p2'].append(p2)
                        aux['h1'].append(h1)
                        aux['h2'].append(h2)
                        aux['total_waste'].append(total_waste)

                        time = self.time_h()

                        time[h1] = self.collection[h1].change_time(p2, self.routes()[h1].index(p1))['new_time']
                        time[h2] = self.collection[h2].change_time(p1, self.routes()[h2].index(p2))['new_time']

                        aux['total_time'].append(sum(time))
                        aux['max_time'].append(max(time))

        aux = pd.DataFrame(aux)
        aux = aux[aux['max_time'] <= self.max_time]
        aux.sort_values(by=['total_waste'], inplace=True, ascending=False)
        self.waste_swap = aux.reset_index(drop=True)

    def calculate_waste_change(self):

        aux = {'p1': [], 'p2': [], 'h': [], 'total_waste': [], 'total_time': [], 'max_time': []}
        for h in self.h():
            for p1 in self.routes()[h][1:-1]:
                for p2 in [p for p in self.waste_collection.pickup_points if p not in self.routes()[h]]:
                    aux['p1'].append(p1)
                    aux['p2'].append(p2)
                    aux['h'].append(h)

                    total_waste = self.waste_collected()

                    total_waste -= self.waste_collected_point_h(p1, self.h_with_point(p1))

                    new_h1 = [h_aux for h_aux in self.h_with_point(p1) if h_aux != h]
                    total_waste += self.waste_collected_point_h(p1, new_h1)

                    new_h2 = self.h_with_point(p2)
                    total_waste -= self.waste_collected_point_h(p2, new_h2)

                    new_h2.append(h)
                    new_h2.sort()

                    total_waste += self.waste_collected_point_h(p2, new_h2)

                    aux['total_waste'].append(total_waste)

                    time = self.time_h()

                    time[h] = self.collection[h].change_time(p2, self.routes()[h].index(p1))['new_time']

                    aux['total_time'].append(sum(time))
                    aux['max_time'].append(max(time))

        aux = pd.DataFrame(aux)
        aux = aux[aux['max_time'] <= self.max_time]
        aux.sort_values(by=['total_waste'], inplace=True, ascending=False)
        self.waste_change = aux.reset_index(drop=True)

    def repair_time_constraint(self):
        h_to_fix = [h for h in self.h() if self.time_h()[h] > self.max_time]
        for h in h_to_fix:
            while self.time_h()[h] > self.max_time:
                worst_p = self.routes()[h][1]
                worst_inc = 100
                for p in self.routes()[h][1:-1]:
                    new_h = self.h_with_point(p)
                    new_h.remove(h)
                    inc = self.waste_collected_point_h(p, self.h_with_point(p)) - self.waste_collected_point_h(p, new_h)
                    if inc < worst_inc:
                        worst_p = p
                        worst_inc = inc
                self.remove_point(h, self.routes()[h].index(worst_p))

    def refine(self):

        for h in range(self.horizon):
            #print(h)
            ruta0 = self.collection[h]

            ruta_orig = ruta0.route()

            best = ruta_orig.copy()
            best_time = ruta0.time()
            #print(best_time)

            mejora = True
            while mejora:
                mejora = False
                ruta_orig = best.copy()
                for i1 in range(1, len(ruta_orig) - 1):
                    for i2 in range(i1, len(ruta_orig) - 1):
                        ruta_aux = ruta_orig.copy()
                        ruta_aux[i1] = ruta_orig[i2]
                        ruta_aux[i2] = ruta_orig[i1]
                        mi = Route(self.waste_collection, self.orig, self.dest, ruta_aux)
                        if mi.time() < best_time:
                            mejora = True
                            #print(mi.time())
                            best = ruta_aux.copy()
                            best_time = mi.time()
            self.update_route(h, best)



