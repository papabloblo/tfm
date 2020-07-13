import random
import numpy as np
import copy

class NeighborhoodAdd:
    def add_random(self):
        for i in range(5):
            random_h = random.choice(self.h())
            random_point = random.choice(self.available_points(h=random_h))
            random_position = random.choice(self.available_add_positions(h=random_h))

            self.add_point(random_point, random_h, random_position)
            self.ImprovePath(random_h)
            self.tabu.update(self.routes())

            if not self.time_constraint():
                self.repair_time_constraint()

            self.update_waste_add(points=[random_point], h=[random_h])
            self.update_waste_swap(h=[random_h])
            self.calculate_waste_change(random_h, random_point)
            #self.update_time_add()

    def update_time(self):
        time_constraint = False
        while not time_constraint and not self.waste_add.empty:
            max_waste = self.waste_add['waste'].max()

            rows_to_update = self.waste_add[(self.waste_add['waste'] == max_waste) &
                                        (self.waste_add['time'] == -1)
                                    ]

            for ind in rows_to_update.index:
                point = rows_to_update.loc[ind, 'point']
                h = rows_to_update.loc[ind, 'h']

                routes = self.routes()

                routes[h] = [routes[h][0], point] + routes[h][1:]

                #time_saved = self.Improve(routes, h=[h])

                time_saved = self.time_h()

                #time_saved[h] = self.time_aux(self.linkern(routes[h]))
                time_saved[h] = self.time_aux(routes[h])

                if max(time_saved) > self.max_time:
                    self.waste_add.drop(ind, inplace=True)
                else:
                    self.waste_add.loc[ind, 'time'] = sum(time_saved)

            if max_waste == self.waste_add['waste'].max():
                time_constraint = True

    def add_best(self):
        while True:

            self.update_time()

            if self.waste_add.empty:
                break

            aux = self.waste_add[(self.waste_add['waste'] == self.waste_add['waste'].max())]
            #aux = aux[(aux['time'] == aux['time'].min())]

            ind = random.choice(aux.index)

            point = aux.loc[ind, 'point']
            h = aux.loc[ind, 'h']

            self.add_point(point, h, position=0)
            self.ImprovePath(h)

            self.waste_add.drop(ind, inplace=True)

            self.update_waste_add(points=[point], h=[h])
            self.update_waste_swap(h=[h])
            self.calculate_waste_change(h, point)
            self.tabu.update(self.routes())

            #print(self.waste_collected())

class NeighborhoodSwap:

    def swap_random(self):
        for i in range(5):
            r = self.routes()

            h = [h for h, r in enumerate(r) if len(r) > 2]
            if len(h) > 0:
                h1 = random.choice(h)
                h.remove(h1)
                h2 = random.choice(h)

                pos1 = random.choice(range(1, len(r[h1]) - 1))
                pos2 = random.choice(range(1, len(r[h2]) - 1))

                self.swap_point(h1, h2, pos1, pos2)
                self.ImprovePath(h1)
                self.ImprovePath(h2)

                self.tabu.update(self.routes())

                if not self.time_constraint():
                    self.repair_time_constraint()

                self.update_waste_add()
                self.update_waste_swap()
                self.calculate_waste_change()

    def update_time_swap(self):
        time_constraint = False
        while not time_constraint and not self.waste_swap.empty:
            max_waste = self.waste_swap['total_waste'].max()

            rows_to_update = self.waste_swap[(self.waste_swap['total_waste'] == max_waste) &
                                            (self.waste_swap['total_time'] == -1)
                                            ]

            for ind in rows_to_update.index:

                p1 = rows_to_update.loc[ind, 'p1']
                h1 = rows_to_update.loc[ind, 'h1']
                p2 = rows_to_update.loc[ind, 'p2']
                h2 = rows_to_update.loc[ind, 'h2']

                routes = self.routes()

                routes[h1][routes[h1].index(p1)] = p2
                routes[h2][routes[h2].index(p2)] = p1
                #times = [self.time_aux(r) for r in routes]

                times = self.time_h()

                #times[h1] = self.time_aux(self.linkern(routes[h1]))
                #times[h2] = self.time_aux(self.linkern(routes[h2]))

                times[h1] = self.time_aux(routes[h1])
                times[h2] = self.time_aux(routes[h2])

                #times = self.Improve(routes, h=[h1, h2])

                if max(times) > self.max_time:
                    self.waste_swap.drop(ind, inplace=True)
                else:
                    self.waste_swap.loc[ind, 'total_time'] = sum(times)

            if max_waste == self.waste_swap['total_waste'].max():
                time_constraint = True

    def swap_best(self):

        while not self.waste_swap.empty:

            self.update_time_swap()

            if self.waste_swap.empty:
                break

            aux = self.waste_swap[(self.waste_swap['total_waste'] == self.waste_swap['total_waste'].max())]
            #aux = aux[(aux['total_time'] == aux['total_time'].min())]

            ind = random.choice(aux.index)

            p1 = aux.loc[ind, 'p1']
            h1 = aux.loc[ind, 'h1']
            p2 = aux.loc[ind, 'p2']
            h2 = aux.loc[ind, 'h2']

            self.change_point(p2, h1, self.routes()[h1].index(p1))
            self.change_point(p1, h2, self.routes()[h2].index(p2))

            self.ImprovePath(h1)
            self.ImprovePath(h2)

            self.update_waste_add(points=[p1, p2], h=[h1, h2])
            self.update_waste_swap(h=[h1, h2])
            self.calculate_waste_change()
            self.tabu.update(self.routes())

            #print(self.waste_collected())


class NeighborhoodChange:

    def change_random(self):
        for i in range(5):
            r = self.routes()

            h = [h for h, r in enumerate(r) if len(r) > 2]

            if len(h) > 0:
                h = random.choice(h)

                pos = random.choice(range(1, len(r[h]) - 1))
                points = [p for p, h_aux in self.points_h_available().items() if h in h_aux]
                points = [p for p in points if p != r[h][pos]]
                p_new = random.choice(points)
                p_old = self.routes()[h][pos]
                self.change_point(p_new, h, pos)
                self.ImprovePath(h)
                #self.update_route(h, self.ImprovePath(self.routes()[h], alpha=10))

                self.tabu.update(self.routes())

                self.update_waste_add()
                self.update_waste_swap()
                #self.update_waste_add(points=[p_new, p_old], h=[h])


                #self.update_time_add()

    def update_time_change(self):
        time_constraint = False
        while not time_constraint and not self.waste_change.empty:
            max_waste = self.waste_change['total_waste'].max()

            rows_to_update = self.waste_change[(self.waste_change['total_waste'] == max_waste) &
                                             (self.waste_change['total_time'] == -1)
                                             ]

            for ind in rows_to_update.index:

                p1 = rows_to_update.loc[ind, 'p1']
                h = rows_to_update.loc[ind, 'h']
                p2 = rows_to_update.loc[ind, 'p2']


                routes = self.routes()

                routes[h][routes[h].index(p1)] = p2

                times = self.time_h()

                times[h] = self.time_aux(routes[h])
                #times[h] = self.time_aux(self.linkern(routes[h]))

                if max(times) > self.max_time:
                    self.waste_change.drop(ind, inplace=True)
                else:
                    self.waste_change.loc[ind, 'total_time'] = sum(times)
                    self.waste_change.loc[ind, 'max_time'] = max(times)

            if max_waste == self.waste_change['total_waste'].max():
                time_constraint = True


    def change_best(self):


        while not self.waste_change.empty:
            print(self.waste_collected())
            self.update_time_change()

            current_waste = self.waste_collected()
            #print(current_waste)
            aux = self.waste_change[self.waste_change['total_waste'] == self.waste_change['total_waste'].max()]
            #aux = aux[aux['total_time'] == aux['total_time'].min()]

            ind = random.choice(aux.index)

            if aux['total_waste'][ind] <= current_waste:
                break

            p1 = aux['p1'][ind]
            h = aux['h'][ind]
            p2 = aux['p2'][ind]


            self.change_point(p2, h, self.routes()[h].index(p1))
            self.ImprovePath(h)

            self.tabu.update(self.routes())


            self.update_waste_add(points=[p1, p2],h=[h])
            self.update_waste_swap(h=[h])

            self.calculate_waste_change(h, p1)





