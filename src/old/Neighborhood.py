import pandas as pd
import random
import time
from Tabu import Tabu

class Neighborhood(Tabu):
    def __init__(self, collection, best_collection):
        super().__init__()
        self.collection = collection
        self.best_collection = best_collection
        #self.tabu_list = {}
        #self.waste_add = self.waste_add_ini()

    def tabu_p_h(self, p, h):
        tabu = False
        if p in self.tabu().keys():
            tabu = h in self.tabu()[p]
        return tabu

    def points_h_available(self, new_collection=None):
        """

        :param new_collection:
        :return: dictionary with points and h available
        """
        if new_collection is None:
            new_collection = self.collection.copy()

        pickup_points = self.collection.waste_collection.pickup_points
        h_p = {}
        for p in pickup_points:
            h_aux = new_collection.h_without_point(p)
            if p in self.tabu():
                h_aux = [h for h in h_aux if h not in self.tabu()[p]]

            if len(h_aux) > 0:
                h_p[p] = h_aux

        return h_p

    def points_add_h_available(self, new_collection=None):
        '''
        Tengo dudas de que se cumpla la desigualdad triangular:
            d(a, b) <= d(a,c) + d(c, b)
        :param new_collection:
        :return:
        '''
        if new_collection is None:
            new_collection = self.collection
        points = self.points_h_available()
        points2 = self.points_h_available()
        for p, h in points.items():
            h2 = []
            for h_aux in h:
                min_time = self.collection.waste_collection.min_time_point(p, new_collection.routes()[h_aux])
                if min_time + new_collection.total_time() <= self.collection.max_time:
                    h2.append(h_aux)
            if len(h2) > 0:
                points2[p] = h2
            else:
                del points2[p]
        return points

    def waste_add(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection.copy()

        #points_h_available = self.points_h_available(new_collection)
        points_h_available = self.points_h_available(new_collection)
        waste = {'point': [], 'h': [], 'waste': []}
        for p, h in points_h_available.items():

            h_w = new_collection.add_point_waste_collected(p, h=h)
            waste['point'] += [p]*len(h_w)
            waste['h'] += h_w.keys()
            waste['waste'] += h_w.values()

        waste = pd.DataFrame(waste)
        waste.sort_values(by=['waste'], inplace=True, ascending=False)
        waste = waste.reset_index(drop=True)
        return waste

    def add_best_neighbors(self, new_collection=None, random_choice=False):
        if new_collection is None:
            new_collection = self.collection.copy()
        best = new_collection.copy()
        x = False
        #print(self.points_h_available())
        if new_collection.time_constraint():

            w = self.waste_add(new_collection)
            routes = new_collection.routes()
            #print(self.tabu_list)
            new_routes = []
            best_point = None

            for waste in w['waste'].unique():
                w_aux = w[w['waste'] == waste]
                #print(w_aux)
                if random_choice:
                    rows = [random.choice(w_aux.index)]
                else:
                    rows = w_aux.index

                for i in rows:

                    point = w.loc[i, 'point']
                    h = w.loc[i, 'h']

                    new_routes2 = []
                    for pos in range(len(routes[h]) - 1):
                        new_route = new_collection.copy()
                        new_route.add_point(point, h, pos)

                        new_routes2.append(new_route)
                        if new_route.time_constraint():
                            if new_route.waste_collected() > best.waste_collected():
                                best = new_route.copy()
                                best_point = point
                                x = True
                                #print(best_point)
                                #self.add_tabu({p: list(range(best.horizon)) for p in best.waste_collection.pickup_points if p != point})
                                #self.add_tabu({point: [h]})


                            elif new_route.waste_collected() == best.waste_collected() and new_route.total_time() < best.total_time():
                                best = new_route.copy()
                                best_point = point
                                x = True
                                #self.add_tabu(
                                 #   {p: list(range(best.horizon)) for p in best.waste_collection.pickup_points
                                  #   if p != point})
                                #self.add_tabu({point: [h]})
                        else:
                            self.add_tabu({point: list(range(best.horizon))})
                    #new_collection = best.copy()



                    #new_routes2 = self.filter_routes_time_constraint(new_routes2)
                    #if len(new_routes2) == 0:
                     #   self.update_tabu_list({point: [h]})
                        #self.add_tabu({point: list(range(self.collection.horizon))})
                    #else:
                     #   new_routes += new_routes2

                #new_routes = self.filter_routes_time_constraint(new_routes)
                if x:
                    # if best_point is not None:
                    #
                    #     w = self.waste_add(best)
                    #     w = w[w['point'] == best_point]
                    #     if len(w) > 0:
                    #         w_aux = w[w['waste'] == max(w['waste'])]
                    #         rows = w_aux.index
                    #         for i in rows:
                    #
                    #             point = w.loc[i, 'point']
                    #             h = w.loc[i, 'h']
                    #
                    #             new_routes2 = []
                    #             for pos in range(len(routes[h]) - 1):
                    #                 new_route = best.copy()
                    #                 new_route.add_point(point, h, pos)
                    #
                    #                 new_routes2.append(new_route)
                    #                 if new_route.time_constraint():
                    #                     if new_route.waste_collected() > best.waste_collected():
                    #                         best = new_route.copy()
                    #                         best_point = point
                    #                         x = True
                    #                         # print(best_point)
                    #                         # self.add_tabu({p: list(range(best.horizon)) for p in best.waste_collection.pickup_points if p != point})
                    #                         # self.add_tabu({point: [h]})
                    #
                    #
                    #                     elif new_route.waste_collected() == best.waste_collected() and new_route.total_time() < best.total_time():
                    #                         best = new_route.copy()
                    #                         best_point = point
                    #                         x = True
                    #                         # self.add_tabu(
                    #                         #   {p: list(range(best.horizon)) for p in best.waste_collection.pickup_points
                    #                         #   if p != point})
                    #                         # self.add_tabu({point: [h]})
                    #
                    #     # if len(self.points_h_available().keys()) == 1:
                    #     #     self.add_tabu({best_point: list(range(best.horizon))})
                    #     # #print(self.points_h_available())
                    #     # else:
                    #     #     self.add_tabu(
                    #     #         {p: list(range(best.horizon)) for p in best.waste_collection.pickup_points if
                    #     #          p != best_point}, self.max_tabu - 1)
                    self.add_tabu({best_point: list(range(best.horizon))})
                    break
        else:
            best = new_collection
        #if len(new_routes) == 0:
         #   new_routes = [new_collection]
        #new = self.tiebreaker(new_routes)

        return best

    def random_add_point(self):
        points_h_available = self.points_h_available()
        new_route = self.collection.copy()

        random_point = random.choice(list(points_h_available.keys()))
        random_h = random.choice(points_h_available[random_point])

        route = self.collection.routes()[random_h]
        position = random.choice(range(len(route) - 1))

        new_route.add_point(random_point, random_h, position)

        return new_route

    def swap_best_neighbors(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection.copy()
        #self.tabu_list = {}
        candidate = new_collection.copy()
        if not candidate.time_constraint():
            H1 = [h for h in range(candidate.horizon) if candidate.time_h()[h] > candidate.max_time]
            if len(H1) > 1:
                H2 = H1.copy()
            else:
                H2 = list(range(candidate.horizon))
        else:
            H1 = list(range(candidate.horizon))
            H2 = H1.copy()
        print(H1)
        print(H2)
        w = self.best_collection.waste_collected()
        total_time = self.best_collection.total_time()
        w = self.best_collection.waste_collected()
        total_time = self.best_collection.total_time()
        while len(H1) > 0:
            h1 = H1.pop()

            H2.remove(h1)
            r1 = candidate.routes()[h1]
            for pos1 in range(1, len(r1)-1):
                p1 = r1[pos1]
                if self.tabu_p_h(p1, h1):
                    continue
                for h2 in H2:

                #for h2 in range(h1+1, candidate.horizon):

                    r2 = candidate.routes()[h2]
                    for pos2 in range(1, len(r2) - 1):
                        p2 = r2[pos2]
                        if p1 == p2 or self.tabu_p_h(p2, h2):
                            continue

                        new = candidate.copy()
                        new.swap_point(h1, h2, pos1, pos2)
                        if new.time_constraint():
                            if new.waste_collected() > w:
                                candidate = new
                                w = new.waste_collected()
                                total_time = candidate.total_time()
                                self.delete_h([h1, h2])
                            elif new.waste_collected() == w and new.total_time() < total_time:
                                candidate = new
                                w = new.waste_collected()
                                total_time = candidate.total_time()
                                self.delete_h([h1, h2])

            #if candidate.waste_collected() > new_collection.waste_collected():
            #    break

        return candidate

    def random_swap_point(self):
        new_route = self.collection.copy()
        r = new_route.routes()

        h = [h for h, r in enumerate(r) if len(r) > 2]
        if len(h) > 0:
            h1 = random.choice(h)
            h.remove(h1)
            h2 = random.choice(h)

            pos1 = random.choice(range(1, len(r[h1])-1))
            pos2 = random.choice(range(1, len(r[h2])-1))

            new_route.swap_point(h1, h2, pos1, pos2)
        return new_route

    def change_best_neighbors(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection.copy()

        candidate = new_collection.copy()
        if not candidate.time_constraint():
            H = [h for h in range(candidate.horizon) if candidate.time_h()[h] > candidate.max_time]
            w = self.best_collection.waste_collected()
            total_time = self.best_collection.total_time()
        else:
            H = list(range(candidate.horizon))
            w = candidate.waste_collected()
            total_time = candidate.total_time()
        H.reverse()
        print(H)
        i = 0
        for h in H:
            if len(candidate.routes()[h]) == 2:
                continue

            for pos in range(1, len(candidate.routes()[h])-1):

                for p in self.points_h_available():
                    if not self.tabu_p_h(p, h) and p not in candidate.routes()[h]:
                        i += 1


                        new = candidate.copy()
                        new.change_point(p, h, pos)

                        if new.time_constraint():

                            if new.waste_collected() > w:
                                print(new.waste_collected() - w)
                                candidate = new.copy()
                                w = new.waste_collected()
                                total_time = candidate.total_time()
                                self.add_tabu({p: list(range(new.horizon))})
                                #self.delete_h([h])

                            elif new.waste_collected() == w and new.total_time() < total_time:
                                candidate = new.copy()
                                w = new.waste_collected()
                                total_time = candidate.total_time()
                                self.add_tabu({p: list(range(new.horizon))})
                                #self.delete_h([h])

        return candidate

    def random_change_point(self):
        new_route = self.collection.copy()
        r = new_route.routes()

        h = [h for h, r in enumerate(r) if len(r) > 2]

        if len(h) > 0:
            h = random.choice(h)

            pos = random.choice(range(1, len(r[h]) - 1))
            points = [p for p, h_aux in self.points_h_available().items() if h in h_aux]
            points = [p for p in points if p != r[h][pos]]
            p = random.choice(points)
            new_route.change_point(p, h, pos)
        return new_route

    def remove_best_neighbors(self, new_collection=None):
        if new_collection is None:
            new_collection = self.collection.copy()

        candidate = new_collection.copy()

        H = [h for h in range(candidate.horizon) if candidate.time_h()[h] > candidate.max_time and len(candidate.routes()[h]) > 2]

        news = [self.best_collection]
        for h in H:
            news2 = []
            for pos in range(1, len(candidate.routes()[h]) - 2):
                new = candidate.copy()
                new.remove_point(h, pos)
                if new.time_h()[h] <= new.max_time:
                    news2.append(new)

            news2 = self.tiebreaker(news2)
            if not self.collection.time_constraint():
                candidate = news2.copy()
            if news2.time_constraint():
                news.append(news2)


        candidate = self.tiebreaker(news)

        return candidate

    def random_remove(self):
        new_route = self.collection.copy()
        r = new_route.routes()

        h = [h for h, r in enumerate(r) if len(r) > 2]

        if len(h) > 0:
            h = random.choice(h)

            pos = random.choice(range(1, len(r[h]) - 1))

            new_route.remove_point(h, pos)

        return new_route

    def filter_routes_time_constraint(self, collection):
        return [r for r in collection if r.time_constraint() is True]

    def tiebreaker(self, new_collection):

        if len(new_collection) > 1:
            #w = [r.diff_waste_collected() for r in new_collection]
            #new_collection = [r for i, r in enumerate(new_collection) if w[i] == max(w)]

            t = [sum(r.time_h()) for r in new_collection]

            new_collection = [r for r in new_collection if sum(r.time_h()) == min(t)]

        new_collection = random.choice(new_collection)

        return new_collection

    def fix_time_constraint(self, new_collection):

        H = [h for h in range(new_collection.horizon) if new_collection.time_h()[h] > new_collection.max_time]
        t = time.time()
        news = []
        while len(H) > 0:
            h = H[0]
            for pos in range(1, len(new_collection.routes()[h])-1):
                new = new_collection.copy()
                new.remove_point(h, pos)
                if len(H) > 1:
                    h2 = H[1]

                    for pos2 in range(1, len(new_collection.routes()[h2]) - 1):

                        new3 = new.copy()
                        new3.remove_point(h2, pos2)
                        if new3.time_constraint():
                            news.append(new3)
                else:
                    if new.time_constraint():
                        news.append(new)

            H.remove(h)
        new = self.tiebreaker(news)
        return new


class NeighborhoodAdd:
    def random(self, route):

        points_h_available = self.points_h_available()
        new_route = self.collection.copy()

        random_point = random.choice(list(points_h_available.keys()))
        random_h = random.choice(points_h_available[random_point])

        route = self.collection.routes()[random_h]
        position = random.choice(range(len(route) - 1))

        new_route.add_point(random_point, random_h, position)

        return new_route