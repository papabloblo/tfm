from itertools import chain

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

    def add_point(self, point, position):
        if position >= len(self.__route)-1:
            raise Exception("No se puede añadir un punto después del destino")

        new_route = list(self.__route[0:position + 1]) + [point] + list(self.__route[position+1:])

        time = self.__time

        time -= self.waste.time_points(self.__route[position], self.__route[position+1])

        time += self.waste.time_points(new_route[position], new_route[position+1])
        time += self.waste.time_points(new_route[position+1], new_route[position + 2])

        self.__route = new_route
        self.__time = time

    def change_point(self, point, position):
        if position == 0 or position == len(self.__route):
            raise Exception("No se pude modificar el destino o el origen")

        new_route = self.__route.copy()
        new_route[position] = point

        time = self.__time

        time -= self.waste.time_points(self.__route[position - 1], self.__route[position])
        time -= self.waste.time_points(self.__route[position], self.__route[position + 1])

        time += self.waste.time_points(new_route[position - 1], new_route[position])
        time += self.waste.time_points(new_route[position], new_route[position + 1])

        self.__route = new_route
        self.__time = time

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




class RouteCollection:

    def __init__(self,
                 waste_collection,
                 orig,
                 dest,
                 horizon=6,
                 routes=None,
                 max_time=6.5*60*60):
        self.waste_collection = waste_collection
        self.horizon = horizon
        self.orig = orig
        self.dest = dest
        self.collection = self.create(routes)
        self.waste_collected_point = self.calculate_waste_collected_point()
        self.max_time = max_time

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
        return RouteCollection(self.waste_collection,
                               self.orig,
                               self.dest,
                               self.horizon,
                               routes=self.routes()
                               )

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
        return list(set(chain(*self.routes())))

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
                waste += min(1, self.waste_collection.fill_level(point, d) + fill_ini)
            else:
                d = h[i] - h[i - 1]
                waste += self.waste_collection.fill_level(point, d)
        return waste

    def point_h2(self, point):
        return [h for h, r in enumerate(self.routes()) if point in r]

    def point_h(self):
        return {p: self.point_h2(p) for p in self.unique_points()}

    def calculate_waste_collected_point(self):
        return {p: self.waste_collected_point_h(p, self.point_h2(p)) for p in self.unique_points()}

    def update_waste_collected_point(self):
        self.waste_collected_point = self.calculate_waste_collected_point()

    def waste_collected(self, waste_collected=None):
        if waste_collected is None:
            waste_collected = self.waste_collected_point

        return sum(waste_collected.values())

    def add_point_h_waste_collected(self, point, h):

        waste_collected = self.waste_collected_point.copy()

        h_orig = self.point_h2(point)
        if h not in h_orig:
            h = h_orig + [h]
        h.sort()

        waste_collected[point] = self.waste_collected_point_h(point, h)

        return self.waste_collected(waste_collected)

    def add_point_waste_collected(self, point, h=None):
        if h is None:
            h = self.point_h_available(point)
        return {h2: self.add_point_h_waste_collected(point, h2) for h2 in h}

    def h_without_point(self, point):
        routes = self.routes()
        return [h for h, r in enumerate(routes) if point not in r]

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

    def time_constraint(self, route):
        return max(route.time_h()) <= self.max_time

    def filter_routes_time_constraint(self, routes):
        return [r for r in routes if self.time_constraint(r) is True]


