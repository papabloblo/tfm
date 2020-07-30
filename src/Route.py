from itertools import chain
import pandas as pd

from Neighborhood2 import NeighborhoodAdd, NeighborhoodChange, NeighborhoodSwap

from Tabu import Tabu


class Route:
    def __init__(self, waste_collection, orig, dest, route=None, max_time=6.5*60*60):
        self.waste = waste_collection
        self.max_time = max_time
        self.orig = orig
        self.dest = dest

        if route is None:
            route = [self.orig, self.dest]

        self.route = route.copy()
        self.time = self.calculate_time()

    def calculate_time(self, route=None):
        if route is None:
            route = self.route
        return self.waste.calculate_route_time(route)

    def update(self, new_route):
        if new_route[0] != self.orig and new_route[-1] != self.dest:
            raise Exception("No se puede modificar el origen o el destino")
        self.route = new_route.copy()
        self.time = self.calculate_time()

    def add_point(self, point, position):
        if position >= len(self.route)-1:
            raise Exception("No se puede añadir un punto después del destino")

        new_route = self.route[:position+1] + [point] + self.route[position+1:]

        self.time = self.add_time(point, position)
        self.route = new_route.copy()


        self.Improve()

        self.repair_time_constraint()

    def add_time(self, point, position):
        new_route = self.route[:position + 1] + [point] + self.route[position + 1:]

        new_route = self.Improve(new_route, inplace=False)

        return self.waste.calculate_route_time(new_route)
        # time = self.time
        #
        # time -= self.waste.time_points(self.route[position], self.route[position + 1])
        #
        # time += self.waste.time_points(self.route[position], point)
        # time += self.waste.time_points(point, self.route[position + 1])
        #
        # return time

    def change_point(self, point, position):
        if position == 0 or position == len(self.route):
            raise Exception("No se pude modificar el destino o el origen")

        self.time = self.change_time(point, position)
        self.route[position] = point

        self.Improve()
        self.repair_time_constraint()

    def change_time(self, point, position):
        new_route = self.route.copy()
        new_route[position] = point

        new_route = self.Improve(new_route, inplace=False)

        return self.waste.calculate_route_time(new_route)

        # time = self.time
        #
        # time -= self.waste.time_points(self.route[position - 1], self.route[position])
        # time -= self.waste.time_points(self.route[position], self.route[position + 1])
        #
        # time += self.waste.time_points(self.route[position - 1], point)
        # time += self.waste.time_points(point, self.route[position + 1])
        #
        # return time

    def remove_point(self, position):
        if position == 0 or position == len(self.route):
            raise Exception("No se pude modificar el destino o el origen")

        self.time = self.remove_time(position)
        del self.route[position]

        self.Improve()
        self.repair_time_constraint()

    def remove_time(self, position):

        time = self.time

        time -= self.waste.time_points(self.route[position - 1], self.route[position])
        time -= self.waste.time_points(self.route[position], self.route[position + 1])

        time += self.waste.time_points(self.route[position - 1], self.route[position+1])

        return time

    def available_points(self):
        return [p for p in self.waste.pickup_points if p not in self.route]

    def available_add_positions(self):
        return list(range(len(self.route)-1))

    def LinKernighan(self, route, R, depth=1, alpha=2):

        if depth < alpha:
            for i, p in enumerate(route[:-1]):
                if p in R:
                    continue
                new_tour = route[:i + 1]
                aux_tour = route[i + 1:-1]
                aux_tour.reverse()
                new_tour += aux_tour
                new_tour.append(route[-1])

                if self.waste.calculate_route_time(new_tour) < self.waste.calculate_route_time(route):
                    return new_tour
                else:
                    new_R = R + [p]
                    new_tour = self.LinKernighan(new_tour, R=new_R, depth=depth + 1, alpha=alpha)
                    if self.waste.calculate_route_time(new_tour) < self.waste.calculate_route_time(route):
                        return new_tour
            return route
        else:
            return route

    def Improve(self, route=None, inplace=True):
        if route is None:
            route = self.route.copy()

        inc_time = True
        while inc_time:
            ini_time = self.waste.calculate_route_time(route)
            route = self.LinKernighan(route, R=[])
            if self.waste.calculate_route_time(route) >= ini_time:
                inc_time = False
        if inplace:
            self.update(route)
        else:
            return route

    def repair_time_constraint(self):
        """
        Repair time constraint. Remove furthest pickup point.
        """
        if self.time > self.max_time:
            time_constraint = True
            while time_constraint:
                time_ini = self.waste.calculate_route_time(self.route)
                for p in self.route[1:-1]:
                    route_aux = self.route.copy()
                    route_aux.remove(p)
                    if self.waste.calculate_route_time(route_aux) < time_ini:
                        time_ini = self.waste.calculate_route_time(route_aux)
                        best_p = p
                self.remove_point(self.route.index(best_p))
                self.Improve()
                if self.time < self.max_time:
                    time_constraint = False


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

        self.collection = self.create_routes(routes)

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

        #self.calculate_waste_change(first_time=True)

    def unique_points(self):
        points = list(set(chain(*self.routes())))
        return [p for p in points if p in self.waste_collection.pickup_points]

    def H(self):
        return list(range(self.horizon))

    def h_with_point(self, point):
        return [h for h, r in enumerate(self.routes()) if point in r]

    def h_without_point(self, point):
        return [h for h, r in enumerate(self.routes()) if point not in r]

    def point_h(self):
        point_h = {}
        for p in self.unique_points():
            point_h[p] = self.h_with_point(p)
        return point_h

    def waste_collected(self):
        point_h = self.point_h()
        total_waste = 0
        for p, H in point_h.items():
            total_waste += self.waste_collection.waste_by_point(p, H)
        return total_waste

    def available_points(self, h):
        return self.collection[h].available_points()

    def available_add_positions(self, h):
        return self.collection[h].available_add_positions()

    def create_routes(self, routes):

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
        return [r.route.copy() for r in self.collection]

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

    def remove_point(self, h, position):
        self.collection[h].remove_point(position)
        self.update_waste_collected_point()

    def update_route(self, h, new_route):
        self.collection[h].update(new_route)
        self.update_waste_collected_point()

    def time_h(self):
        return [r.time for r in self.collection]








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

    def calculate_waste_collected_point(self):
        return {p: self.waste_collected_point_h(p, self.h_with_point(p)) for p in self.unique_points()}

    def update_waste_collected_point(self):
        self.waste_collected_point = self.calculate_waste_collected_point()

    def diff_waste_collected(self):
        w = {p: self.waste_collection.real_fill_level(p, max(h)) - self.waste_collected_point[p] for p, h in self.point_h().items()}
        return sum(w.values())

    def add_point_h_waste_collected(self, point, h):

        waste_collected = self.waste_collected_point.copy()

        h_orig = self.h_with_point(point)
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
        total_waste_orig = self.waste_collected()
        for h1 in h:
            for h2 in range(self.horizon):
                if h2 == h1 or [h2, h1] in visited_h or [h1, h2] in visited_h:
                    continue

                for p1 in self.routes()[h1]:
                    total_waste = total_waste_orig
                    total_waste -= self.waste_collected_point_h(p1, self.h_with_point(p1))

                    for p2 in self.routes()[h2]:
                        if p1 in self.routes()[h2] or p2 in self.routes()[h1]:
                            continue
                        if len(self.routes()[h1]) == 2 or len(self.routes()[h2]) == 2:
                            continue

                        aux['p1'].append(p1)
                        aux['p2'].append(p2)
                        aux['h1'].append(h1)
                        aux['h2'].append(h2)

                        total_waste_aux = total_waste

                        total_waste_aux -= self.waste_collected_point_h(p2, self.h_with_point(p2))

                        new_h_p1 = [h for h in self.h_with_point(p1) if h != h1]
                        new_h_p1.append(h2)
                        new_h_p1.sort()

                        new_h_p2 = [h for h in self.h_with_point(p2) if h != h2]
                        new_h_p2.append(h1)
                        new_h_p2.sort()

                        total_waste_aux += self.waste_collected_point_h(p1, new_h_p1)
                        total_waste_aux += self.waste_collected_point_h(p2, new_h_p2)

                        aux['total_waste'].append(total_waste_aux)
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
            h_aux = self.H()
        else:
            h_aux = [h]

        total_waste_orig = self.waste_collected()

        aux = {'p1': [], 'p2': [], 'h': [], 'total_waste': [], 'total_time': [], 'max_time': []}
        for h in h_aux:
            for p1 in self.routes()[h][1:-1]:
                candidate_points = [point for point in self.waste_collection.pickup_points if point not in self.routes()[h]]

                total_waste = total_waste_orig
                total_waste -= self.waste_collected_point_h(p1, self.h_with_point(p1))

                new_h1 = [h_aux for h_aux in self.h_with_point(p1) if h_aux != h]
                total_waste += self.waste_collected_point_h(p1, new_h1)

                for p2 in candidate_points:
                    aux['p1'].append(p1)
                    aux['p2'].append(p2)
                    aux['h'].append(h)

                    total_waste_aux = total_waste

                    new_h2 = self.h_with_point(p2)
                    total_waste_aux -= self.waste_collected_point_h(p2, new_h2)

                    new_h2.append(h)
                    new_h2.sort()

                    total_waste_aux += self.waste_collected_point_h(p2, new_h2)

                    aux['total_waste'].append(total_waste_aux)

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
           self.collection[h].repair_time_constraint()