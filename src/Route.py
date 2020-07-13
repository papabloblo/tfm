from itertools import chain
import pandas as pd

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

    def time_by_link(self):
        route_time = []
        for i in range(len(self.__route) - 1):
            route_time.append(self.waste.time_points(self.__route[i], self.__route[i+1]))
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
                 waste_swap=None,
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
            self.waste_add = self.calculate_waste_add2()
        else:
            self.waste_add = waste_add
        if waste_swap is None:
            self.update_waste_swap(first_time=True)
        else:
            self.waste_swap = waste_swap

        self.calculate_waste_change(first_time=True)

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
        return [r.route().copy() for r in self.collection]

    def copy(self):
        route = RouteCollection(waste_collection=self.waste_collection,
                               orig=self.orig,
                               dest=self.dest,
                               horizon=self.horizon,
                               routes=self.routes().copy(),
                               waste_add=self.waste_add,
                                waste_swap=self.waste_swap
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
        h.sort()
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

    def inc_waste(self, point, new_h):
        current_h = self.h_with_point(point)
        new_h = current_h + [new_h]

        inc_waste = self.waste_collected_point_h(point, new_h) - \
                    self.waste_collected_point_h(point, current_h)

        return(inc_waste)

    def calculate_waste_add2(self, point=None, h=None):
        points_h_available = self.points_h_available()

        if point is not None:
            points_h_available = {point: points_h_available[point]}

        if h is not None:
            points_h_available_aux = {p: [h] for p, h2 in points_h_available.items() if h in h2}
            if point is not None:
                points_h_available_aux[point] = {point: points_h_available[point]}
            points_h_available = points_h_available_aux


        waste = {'point': [], 'h': [], 'waste': [], 'time': []}
        for p, h in points_h_available.items():
            for h_aux in h:
                waste['point'].append(p)
                waste['h'].append(h_aux)
                waste['waste'].append(self.inc_waste(p, h_aux))
                waste['time'].append(-1)

        waste = pd.DataFrame(waste)

        waste['point'] = waste['point'].astype('int')
        waste['h'] = waste['h'].astype('int')

        waste = waste[waste['waste'] >= 0]
        waste.sort_values(by=['waste'], inplace=True, ascending=False)
        waste = waste.reset_index(drop=True)

        return (waste)

    def update_waste_add(self, points=None, h=None):
        if h is not None:
            for h_aux in h:
                self.waste_add = self.waste_add[self.waste_add['h'] != h_aux]

                self.waste_add = self.waste_add.append(self.calculate_waste_add2(h=h_aux))

        if points is not None:
            for p in points:
                self.waste_add = self.waste_add[self.waste_add['point'] != p]
                self.waste_add = self.waste_add.append(self.calculate_waste_add2(p))

        self.waste_add = self.waste_add[self.waste_add['waste'] >= 0]
        self.waste_add.sort_values(by=['waste'], inplace=True, ascending=False)
        self.waste_add = self.waste_add.reset_index(drop=True)

    def calculate_waste_swap(self, h1, h2, p1, p2):

        total_waste = self.waste_collected()

        total_waste -= self.waste_collected_point_h(p1, self.h_with_point(p1))
        total_waste -= self.waste_collected_point_h(p2, self.h_with_point(p2))

        new_h_p1 = [h for h in self.h_with_point(p1) if h != h1]
        new_h_p1.append(h2)
        new_h_p1.sort()

        new_h_p2 = [h for h in self.h_with_point(p2) if h != h2]
        new_h_p2.append(h1)
        new_h_p2.sort()

        total_waste += self.waste_collected_point_h(p1, new_h_p1)
        total_waste += self.waste_collected_point_h(p2, new_h_p2)

        return total_waste

    def update_waste_swap(self, h=None, first_time=False):

        if h is None:
            h = range(self.horizon)

        aux = {'p1': [], 'p2': [], 'h1': [], 'h2': [], 'total_waste': [], 'total_time' : []}

        visited_h = []

        for h1 in h:
            for h2 in range(self.horizon):
                if h2 == h1 or [h2, h1] in visited_h or [h1, h2] in visited_h:
                    continue

                for p1 in self.routes()[h1]:
                    for p2 in self.routes()[h2]:
                        if p1 in self.routes()[h2] or p2 in self.routes()[h1]:
                            continue
                        if len(self.routes()[h1]) == 2 or len(self.routes()[h2]) == 2:
                            continue

                        aux['p1'].append(p1)
                        aux['p2'].append(p2)
                        aux['h1'].append(h1)
                        aux['h2'].append(h2)

                        aux['total_waste'].append(self.calculate_waste_swap(h1, h2, p1, p2))
                        aux['total_time'].append(-1)
                visited_h.append([h1, h2])
                visited_h.append([h2, h1])

        aux = pd.DataFrame(aux)

        if not first_time:
            for h_aux in h:
                self.waste_swap = self.waste_swap[self.waste_swap['h1'] != h_aux]
                self.waste_swap = self.waste_swap[self.waste_swap['h2'] != h_aux]
            self.waste_swap = self.waste_swap.append(aux)
        else:
            self.waste_swap = aux

        self.waste_swap['p1'] = self.waste_swap['p1'].astype('int')
        self.waste_swap['h1'] = self.waste_swap['h1'].astype('int')

        self.waste_swap['p2'] = self.waste_swap['p2'].astype('int')
        self.waste_swap['h2'] = self.waste_swap['h2'].astype('int')

        self.waste_swap = self.waste_swap[self.waste_swap['total_waste'] - self.waste_collected() > 0]

        self.waste_swap.sort_values(by=['total_waste'], inplace=True, ascending=False)
        self.waste_swap = self.waste_swap.reset_index(drop=True)


    def calculate_waste_change(self, h=None, p=None, first_time=False):

        if h is None:
            h_aux = self.h()
        else:
            h_aux = [h]

        aux = {'p1': [], 'p2': [], 'h': [], 'total_waste': [], 'total_time': [], 'max_time': []}
        for h in h_aux:
            for p1 in self.routes()[h][1:-1]:
                candidate_points = [point for point in self.waste_collection.pickup_points if point not in self.routes()[h]]
                for p2 in candidate_points:
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

                    aux['total_time'].append(-1)
                    aux['max_time'].append(-1)
        if p is not None:
            for h in self.h_with_point(p):
                candidate_points = [point for point in self.waste_collection.pickup_points if point not in self.routes()[h]]
                for p2 in candidate_points:
                    aux['p1'].append(p)
                    aux['p2'].append(p2)
                    aux['h'].append(h)

                    total_waste = self.waste_collected()

                    total_waste -= self.waste_collected_point_h(p, self.h_with_point(p))

                    new_h1 = [h_aux for h_aux in self.h_with_point(p) if h_aux != h]
                    total_waste += self.waste_collected_point_h(p, new_h1)

                    new_h2 = self.h_with_point(p2)
                    total_waste -= self.waste_collected_point_h(p2, new_h2)

                    new_h2.append(h)
                    new_h2.sort()

                    total_waste += self.waste_collected_point_h(p2, new_h2)

                    aux['total_waste'].append(total_waste)

                    aux['total_time'].append(-1)
                    aux['max_time'].append(-1)



        aux = pd.DataFrame(aux)

        if first_time:
            self.waste_change = aux
            self.waste_change.sort_values(by=['total_waste'], inplace=True, ascending=False)
            self.waste_change = self.waste_change.reset_index(drop=True)
        else:
            self.waste_change = self.waste_change[self.waste_change['h'] != h]
            self.waste_change = self.waste_change[self.waste_change['p1'] != p]

            self.waste_change = self.waste_change.append(aux)
            self.waste_change.sort_values(by=['total_waste'], inplace=True, ascending=False)
            self.waste_change = self.waste_change.reset_index(drop=True)

    def repair_time_constraint(self):
        h_to_fix = [h for h in self.h() if self.time_h()[h] > self.max_time]
        for h in h_to_fix:
        #for h in range(self.horizon):
            time_constraint = True
            while time_constraint:
                time_ini = self.time_aux(self.routes()[h])

                for p in self.routes()[h][1:-1]:
                    route_aux = self.routes()[h].copy()
                    route_aux.remove(p)
                    if self.time_aux(route_aux) < time_ini:
                        time_ini = self.time_aux(route_aux)
                        best_p = p
                self.remove_point(h, self.routes()[h].index(best_p))
                self.ImprovePath(h)
                if self.time_h()[h] < self.max_time:
                    time_constraint = False

    def opt_swap(self, route, i, k):
        new_route = route[:i]
        route_aux = route[i:k + 1]
        route_aux.reverse()
        new_route += route_aux + route[k + 1:]
        return (new_route)


    def linkern(self, route, depth=1, R=[], alpha=2):
        if depth < alpha:
            for i, p in enumerate(route[:-1]):
                if p in R:
                    continue
                new_tour = route[:i + 1]
                aux_tour = route[i + 1:-1]
                aux_tour.reverse()
                new_tour += aux_tour
                new_tour.append(route[-1])

                if self.time_aux(new_tour) < self.time_aux(route):
                    return new_tour
                else:

                    new_R = R + [p]
                    new_tour = self.linkern(new_tour, R=new_R, depth=depth + 1, alpha=alpha)
                    if self.time_aux(new_tour) < self.time_aux(route):
                        return (new_tour)
            return (route)
        else:
            return (route)

    def linkern2(self, x):

        for i in range(10):
            # print(self.time_aux(x))
            x = self.linkern(x, depth=1, alpha=3, R=[])
        return(x)

    def ImprovePath(self, h):

        x = self.routes()

        x = self.Improve(x, [h])[h]

        x = self.linkern2(x)
        self.update_route(h, x)



    def ImprovePath_old2(self, h):
        self.ImprovePath_old(h)
        route = self.routes()[h]
        best_distance = self.time_aux(route)
        improvement = False
        while not improvement:
            for i in range(1, len(route)):
                for k in range(i + 1, len(route)-1):
                    new_route = self.opt_swap(route, i, k)
                    new_distance = self.time_aux(new_route)
                    if new_distance < best_distance:
                        route = new_route
                        best_distance = new_distance
                        improvement = True
                        break
                if improvement:
                    break
            if i == len(route) - 1:
                improvement = True
        self.update_route(h, route)
        #self.ImprovePath_old(h)

    def Improve(self, routes, h = None):
        if h is None:
            h = []
        times = []
        routes_aux = [r.copy() for r in routes]
        for h2 in range(self.horizon):
            route = routes[h2]
            if h2 not in h:
                times.append(self.time_aux(route))
            else:
                best_distance = self.time_aux(route)
                improvement = False
                while not improvement:
                    for i in range(1, len(route)):
                        for k in range(i + 1, len(route) - 1):
                            new_route = self.opt_swap(route, i, k)
                            new_distance = self.time_aux(new_route)
                            if new_distance < best_distance:
                                route = new_route
                                best_distance = new_distance
                                improvement = True
                                break
                        if improvement:
                            break
                    if i == len(route) - 1:
                        improvement = True

                times.append(self.time_aux(route))
                routes_aux[h2] = route
        #return(times)

        return(routes_aux)


    def ImprovePath_old(self, h):

        ruta0 = self.collection[h]

        ruta_orig = ruta0.route()

        best = ruta_orig.copy()
        best_time = ruta0.time()

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

    def ImprovePath_old2(self, route):

        route_aux = route.copy()
        best = route.copy()
        best_time = self.time_aux(route)

        mejora = True
        while mejora:
            mejora = False
            for i1 in range(1, len(route_aux) - 1):
                for i2 in range(i1, len(route) - 1):
                    ruta_aux = ruta_orig.copy()
                    ruta_aux[i1] = ruta_orig[i2]
                    ruta_aux[i2] = ruta_orig[i1]
                    mi = Route(self.waste_collection, self.orig, self.dest, ruta_aux)
                    if mi.time() < best_time:
                        mejora = True
                        best = ruta_aux.copy()
                        best_time = mi.time()


    def ImprovePath2(self, route, depth=1, R=None, alpha=2, route_orig=None, max_depth=100):
        if R is None:
            R = []

        if route_orig is None:
            route_orig = route.copy()
        if len(route) > 5:

            edges = self.P(route)
            edges = [x for x in edges if x[0] not in R]
            gain = 0
            if depth < alpha:
                for i, x in enumerate(edges):
                    gain = self.waste_collection.time_points(x[0], x[1]) - \
                           self.waste_collection.time_points(route[-2], x[0])

                    if gain > 0:
                        tour = route[0:i + 1]
                        tour_aux = route[i + 1:-1]
                        tour_aux.reverse()
                        tour += tour_aux
                        tour += [route[-1]]

                        if self.time_aux(tour) < self.time_aux(route_orig):
                            return (tour)
                        else:
                            return(self.ImprovePath(tour, depth + 1, R + [x[0]], alpha, route_orig))
                if gain <= 0:
                    return(route)
            else:
                gain = []
                for i, x in enumerate(edges):
                    gain.append(self.waste_collection.time_points(x[0], x[1]) - \
                                self.waste_collection.time_points(route[-2], x[0]))
                if len(gain) > 0:
                    if max(gain) > 0 and depth < max_depth:
                        best = gain.index(max(gain))
                        tour = route[0:best + 1]
                        tour_aux = route[best + 1:-1]
                        tour_aux.reverse()
                        tour += tour_aux
                        tour += [route[-1]]
                        if self.time_aux(tour) < self.time_aux(route_orig):
                            return (tour)
                        else:
                            return (self.ImprovePath(tour, depth + 1, R + [route[best]], alpha, route_orig))
                    else:
                        if self.time_aux(route) < self.time_aux(route_orig):
                            return (route)
                        else:
                            return (route_orig)
                else:
                    return (route)
        else:
            return(route)


    def refine(self):
        total_time_ini = self.total_time()
        for h in range(self.horizon):
            if len(self.routes()[h]) > 5:
                route_refined = self.ImprovePath(self.routes()[h], alpha=1)
                if route_refined is not None:
                    if self.time_aux(route_refined) < self.time_aux(self.routes()[h]):
                        self.update_route(h, route_refined)
        print('Refinamiento:',  total_time_ini - self.total_time())

    def P(self, r):
        links = []
        for i, t in enumerate(r[:-2]):
            links.append([t, r[i + 1]])
        return links

    def time_aux(self, r):
        route_time = 0
        for i in range(len(r) - 1):
            route_time += self.waste_collection.time_points(r[i], r[i + 1])
        return route_time