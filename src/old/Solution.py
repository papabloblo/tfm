import random
import numpy as np



class Solution:
    def __init__(self, orig, dest, horizon, file_filling_rates, file_times, max_hours=6.5):
        self.WasteCollection = WasteCollection(file_filling_rates, file_times)
        self.RouteCollection = RouteCollection(self.WasteCollection, orig, dest, horizon)
        self.max_time = max_hours*60*60
        self.horizon = horizon


    def forbiden_h_point(self, point):
        times = self.RouteCollection.time_h()
        routes = self.RouteCollection.extract_routes()
        h_for = []
        for h, r in enumerate(routes):
            if times[h] + self.WasteCollection.min_time_point(point, r) > self.max_time:
                h_for.append(h)
        return h_for

    def random_neighbor(self):
        new_route = self.new_collection()

        h = random.choice(range(self.horizon))
        route_h = new_route.extract_routes()[h]

        points = [p for p in self.WasteCollection.pickup_points if p not in route_h]
        point = random.choice(points)

        action = random.choice(['add', 'change', 'remove'])
        if action == 'change' and len(route_h) > 2:
            index = random.choice(range(1, len(route_h) - 1))
            new_route.collection[h].change_point(point, index)
        elif action == 'remove' and len(route_h) > 2:
            index = random.choice(range(1, len(route_h)-1))
            new_route.collection[h].remove_point(index)
        else:
            index = random.choice(range(len(route_h) - 1))
            new_route.collection[h].add_point(point, index)

        return new_route

    def waste_add_point_h(self, points=None, h=None):
        if points is None:
            points = self.WasteCollection.pickup_points
        if h is None:
            h = range(self.horizon)

        h_aux=h
        w = {}
        for p in points:
            h_aux = [h2 for h2 in h if h2 not in solution.forbiden_h_point(p)]
            w[p] = {h2: solution.RouteCollection.new_point_waste_collected(p, h2) for h2 in h_aux}
        return w

    def best_add_point(self, points=None, max_w=1, h=None):
        if points is None:
            points = solution.WasteCollection.pickup_points

        waste_add = solution.waste_add_point_h(points, h)

        best_w = list(set([max(w.values()) for w in waste_add.values()]))
        best_w.sort(reverse=True)
        if max_w - 1 >= len(best_w):
            best_w = best_w[-1]
        else:
            best_w = best_w[max_w - 1]
        w2 = {}
        for p, w in waste_add.items():
            w2[p] = {h: waste for h, waste in w.items() if waste == best_w}
        w2 = {h: w for h, w in w2.items() if w != {}}
        return w2

    def add_point(self, max_w, points, h=None):
        add = solution.best_add_point(max_w=max_w, points=points, h=h)
        new_routes = []
        for p, h in add.items():
            for i in h.keys():
                positions = range(len(solution.RouteCollection.extract_routes()[i]) - 1)
                for pos in positions:
                    new_route = solution.new_collection()
                    new_route.collection[i].add_point(p, pos)
                    new_route.update_w()
                    new_routes.append(new_route)
        return new_routes

    def waste_change_point(self, points=None, h=None):
        if points is None:
            points = self.WasteCollection.pickup_points
        if h is None:
            h = range(self.horizon)

        w_points = solution.RouteCollection.waste_collected_point()
        w_add = solution.waste_add_point_h(h=h)
        w_new = {}
        for p in points:
            w_new[p] = {}
            if p in w_points.keys():
                h = [h2 for h2 in h if h2 not in w_points[p]]

            for p2 in w_points.keys():
                if p2 != p:
                    w_new[p][p2] = {}
                    for h2, w in w_points[p2].items():
                        if h2 in h:
                            w_new[p][p2][h2] = w_add[p][h2] - w
                    if len(w_new[p][p2]) == 0:
                        del w_new[p][p2]
        w_new = {h: w for h, w in w_new.items() if w != {}}
        return w_new

    def best_change_point(self, points=None, max_w=1, h=0):
        if points is None:
            points = self.WasteCollection.pickup_points
        w_change = solution.waste_change_point(points=points, h=h)
        if len(w_change) > 0:
            w = []
            for i in w_change.values():
                for j in i.values():
                    w += j.values()
            w = list(set(w))
            w.sort(reverse=True)

            if max_w - 1 >= len(w):
                w = w[-1]
            else:
                w = w[max_w - 1]

            res = {}
            for p1, w1 in w_change.items():
                res[p1] = {}
                for p2, w2 in w1.items():
                    aux = {h3: w3 for h3, w3 in w2.items() if w3 == w}
                    if len(aux) > 0:
                        res[p1][p2] = aux
                if len(res[p1]) == 0:
                    del res[p1]

        else:
            res = {}
        return res

    def change_point2(self, max_w, points=None, h=0):
        if points is None:
            points = self.WasteCollection.pickup_points
        change = solution.best_change_point(max_w=max_w, points=points, h=h)
        new_routes = []
        for p, h in change.items():
            for p2, h2 in h.items():
                for i in h2.keys():
                    position = solution.RouteCollection.extract_routes()[i]
                    if len(position) > 2:
                        pos = [i for i, p in enumerate(position) if p == p2][0]

                        new_route = solution.new_collection()
                        new_route.collection[i].change_point(p, pos)
                        new_routes.append(new_route)

        return new_routes

    def change_point(self, points=None, h=None):
        routes = solution.RouteCollection.extract_routes()
        new_routes = []
        for h2 in h:
            for pos in range(1, len(routes[h2])-1):
                for p in points:
                    new_route = solution.new_collection()
                    new_route.collection[h2].change_point(p, pos)
                    new_route.update_w()
                    new_routes.append(new_route)
        return new_routes

    def filter_routes_time_constraint(self, routes):
        return [r for r in routes if solution.time_constraint(r) is True]


    def time_constraint(self, route):
        return max(route.time_h()) <= self.max_time

    def best_neighbor(self):

        for i in range(1000):
            max_w = 1
            points = np.random.choice(solution.WasteCollection.pickup_points, size=200, replace=False)

            h = np.random.choice(range(solution.horizon), size=3, replace=False)
            #h = [range(7)[i%7]]
            #h=[1,2]
            print(h)

            print('Tamaño vecindad:', max_w)
            #h = [0]
            #print(max_w)
            mi = NeighborhoodAdd(solution.RouteCollection)
            neighbors = mi.generate_neighbors()

            #neighbors = solution.add_point(max_w=max_w, points=points, h=h)
            neighbors = solution.filter_routes_time_constraint(neighbors)


            #neighbors = [random.choice(neighbors)]
            times = [min(r.time_h()) for r in neighbors]
            neighbors = [n for n in neighbors if min(n.time_h()) == min(times)]

            if len(neighbors) > 0:
                #res = random.choice(neighbors)
                res = neighbors[0]
                solution.RouteCollection = res
                print('Función objetivo:', res.waste_collected())
                print('Tiempos por día:', res.time_h())
                print('Número de visitas por día:', [len(x) for x in solution.RouteCollection.extract_routes()])
                print("")



                max_w += 1




        return res