class Tabu:

    def __init__(self, collection_points, horizon, route, max_tabu=50):
        self.max_tabu = max_tabu
        self.horizon = horizon
        self.collection_points = collection_points
        self.tabu_list = self.intialize()
        self.current_route = route.copy()

    def intialize(self):
        return {p: [-1]*self.horizon for p in self.collection_points}

    def changes(self, route1, route2):
        set_current = set(route1)
        set_new = set(route2)
        return list(set_new.symmetric_difference(set_current))

    def changes_by_h(self, current_route, new_route):
        points_changed = dict.fromkeys(range(self.horizon))
        for h in range(self.horizon):
            points_changed[h] = self.changes(current_route[h], new_route[h])
        points_changed = {h: points for h, points in points_changed.items() if len(points) > 0}
        return points_changed

    def update(self, new_route):
        changes = self.changes_by_h(self.current_route, new_route)

        for p in self.tabu_list.keys():
            for h, n in enumerate(self.tabu_list[p]):
                if n != -1:
                    self.tabu_list[p][h] += 1

        for h, points in changes.items():
            for p in points:
                self.tabu_list[p][h] = 0
        self.current_route = new_route.copy()

    def tabu_by_h(self):
        tabu = {h: [] for h in range(self.horizon)}
        for p, H in self.tabu_list.items():
            for h, n in enumerate(H):
                if n < self.max_tabu and n >= 0:
                    tabu[h].append(p)
        return tabu

    def tabu_p(self, point):
        aux = [h for h, n in enumerate(self.tabu_list[point]) if n < self.max_tabu and n >= 0]

        if len(aux) > 0:
            aux = list(range(self.horizon))
        return aux
