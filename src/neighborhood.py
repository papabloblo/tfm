import pandas as pd
import random

class NeighborhoodAdd:
    def __init__(self, collection):
        self.collection = collection

    def random_neighbor(self):
        random_point = self.collection.random_point_h()

        route = self.collection.routes()[random_point['h']]
        position = random.choice(range(len(route) - 1))

        new_route = self.collection.copy()

        new_route.add_point(random_point['point'], random_point['h'], position)

        return new_route

    def h_point_constraint_time(self, h, point):
        h_new = []
        for h2 in h:
            min_new_time = self.collection.waste_collection.min_time_point(point, routes[h2])
            current_time = self.collection.time_h()[h2]
            if current_time + min_new_time <= self.max_time:
                h_new.append(h2)
        return h_new

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

waste_collection = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                    file_times="data/times-between-pickup-points.txt")

collection = RouteCollection(
    waste_collection, orig=5,
                    dest=5,
                    horizon=7
                    )

neigh = NeighborhoodAdd(collection=collection)

a = neigh.random_neighbor()

a.routes()

collection
collection.new_collection()
class Neighborhood:
    def __init__(self, collection):
        self.collection = collection
        self.add = NeighborhoodAdd(collection)
