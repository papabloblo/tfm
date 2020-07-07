import random
import numpy as np
import copy

class NeighborhoodAdd:
    def add_random(self):

        random_h = random.choice(self.h())
        #for random_h in range(self.horizon):
        random_point = random.choice(self.available_points(h=random_h))
        random_position = random.choice(self.available_add_positions(h=random_h))

        self.add_point(random_point, random_h, random_position)
        self.ImprovePath(random_h)
        #self.update_route(h, self.ImprovePath(self.routes()[h], alpha=1))
        #self.refine()
        self.tabu.update(self.routes())

        if not self.time_constraint():
            self.repair_time_constraint()

        self.update_waste_add(points=[random_point], h=[random_h])
        self.update_waste_swap(h=[random_h])
        #self.update_time_add()


    def add_best(self):
        improvement = False
        #self.update_waste_add()
        #while not improvement and not self.waste_add.empty:# and i < 50 :
        while not self.waste_add.empty:  # and i < 50 :
            current_waste = self.waste_add['waste'].max()

            #print(self.waste_collected())

            aux = self.waste_add[
                (self.waste_add['waste'] == self.waste_add['waste'].max()) & (self.waste_add['time'] == -1)]

            for ind in aux.index:
                point = aux['point'][ind]
                h = aux['h'][ind]
                pos = 0

                routes = copy.deepcopy(self.routes())

                routes[h] = [routes[h][0]] + [point] + routes[h][1:]

                #orig = self.copy()
                #orig.add_point(point, h, pos)
                #orig.ImprovePath(h)

                #time_saved = orig.total_time()

                time_saved = self.Improve(routes, h=[h])

                if max(time_saved) > self.max_time:
                    self.waste_add.drop(ind, inplace=True)
                else:
                    self.waste_add.loc[ind, 'time'] = sum(time_saved)

                #self.waste_add.loc[ind, 'time'] = time_saved

                #if not orig.time_constraint():
                #    self.waste_add.drop(ind, inplace=True)


            aux = self.waste_add[(self.waste_add['waste'] == self.waste_add['waste'].max())]

            if aux['waste'].max() < current_waste or self.waste_add.empty:
                continue

            #print(aux)
            #while not aux.empty:
            aux2 = aux[(aux['time'] == aux['time'].min())]
            aux2 = aux2[aux2['h'] == aux2['h'].max()]
            if aux2['waste'].max() < current_waste or self.waste_add.empty:
                continue
            elif len(aux2.index) == 1:
                ind = aux2.index[0]
            else:
                ind = random.choice(aux2.index)


            point = aux['point'][ind]
            h = aux['h'][ind]
            pos = 0

            self.add_point(point, h, pos)
            self.ImprovePath(h)
            improvement = True
            aux.drop(ind, inplace=True)

            aux = aux[aux['point'] != point]
            aux = aux[aux['h'] != h]
            #self.update_waste_add(points=[point], h=[h])

            self.update_waste_add(points=[point], h=[h])
            self.update_waste_swap(h=[h])

        if improvement:
            self.tabu.update(self.routes())

            self.update_waste_add(points=[point], h=[h])
            self.update_waste_swap(h=[h])

            #self.waste_add = self.waste_add[~((self.waste_add['point'] == point) & (self.waste_add['h'] != h))]



    def add_best_orig(self):

        if self.time_constraint() and not self.waste_add.empty and not self.time_add.empty:

            aux = self.time_add[self.time_add['total_time'] == self.time_add['total_time'].min()]
            if len(aux) > 1:
                aux = aux[aux['h'] == aux['h'].max()]
            ind = random.choice(aux.index)

            point = aux['point'][ind]
            h = aux['h'][ind]
            pos = aux['pos'][ind]

            self.add_point(point, h, pos)
            self.refine()
            self.tabu.update(self.routes())

            self.update_waste_add([point], [h])
            #self.update_time_add(h)


            #while self.time_add.empty and not self.waste_add.empty:
            #    self.waste_add = self.waste_add[self.waste_add['waste'] != max(self.waste_add['waste'])]
             #   self.update_time_add()


class NeighborhoodSwap:

    def swap_random(self):
        r = self.routes()

        h = [h for h, r in enumerate(r) if len(r) > 2]
        if len(h) > 0:
            h1 = random.choice(h)
            h.remove(h1)
            h2 = random.choice(h)

            pos1 = random.choice(range(1, len(r[h1]) - 1))
            pos2 = random.choice(range(1, len(r[h2]) - 1))
            p1 = r[h1][pos1]
            p2 = r[h2][pos2]

            self.swap_point(h1, h2, pos1, pos2)
            self.ImprovePath(h1)
            self.ImprovePath(h2)
            #self.update_route(h1, self.ImprovePath(self.routes()[h1], alpha=1))
            #self.update_route(h2, self.ImprovePath(self.routes()[h2], alpha=1))
            #self.refine()
            self.tabu.update(self.routes())

            if not self.time_constraint():
                self.repair_time_constraint()

            self.update_waste_add()
            self.update_waste_swap()
            #self.update_waste_add(points=[p1, p2], h=[h1,h2])
            #self.update_waste_add(points=[p1, p2], h=h2)
            #self.update_time_add()


    def swap_best(self):
        #if self.waste_swap.empty:
        #self.update_waste_swap()

        improvement = False
        i = 0
        #while i < 10 and not self.waste_swap.empty:  # and i < 50 :
        while not self.waste_swap.empty:  # and i < 50 :

            current_waste = self.waste_swap['total_waste'].max()

            aux = self.waste_swap[
                (self.waste_swap['total_waste'] == current_waste) & (self.waste_swap['total_time'] == -1)]

            for ind in aux.index:

                p1 = aux.loc[ind, 'p1']
                h1 = aux.loc[ind, 'h1']
                p2 = aux.loc[ind, 'p2']
                h2 = aux.loc[ind, 'h2']

                routes = self.routes()

                routes[h1][routes[h1].index(p1)] = p2
                routes[h2][routes[h2].index(p2)] = p1

                times = self.Improve(routes, h=[h1, h2])


                if max(times) > self.max_time:
                    self.waste_swap.drop(ind, inplace=True)
                else:
                    self.waste_swap.loc[ind, 'total_time'] = sum(times)


            aux = self.waste_swap[(self.waste_swap['total_waste'] == self.waste_swap['total_waste'].max())]

            aux = aux[(aux['total_time'] == aux['total_time'].min())]

            aux = aux[(aux['h1'] == aux['h1'].max()) | (aux['h2'] == aux['h2'].max())]

            if aux['total_waste'].max() < current_waste or self.waste_swap.empty:
                continue
            elif len(aux.index) == 1:
                ind = aux.index[0]
            else:
                ind = random.choice(aux.index)

            p1 = aux['p1'][ind]
            p2 = aux['p2'][ind]
            h1 = aux['h1'][ind]
            h2 = aux['h2'][ind]

            inc_waste = self.waste_collected()

            self.change_point(p2, h1, self.routes()[h1].index(p1))
            self.change_point(p1, h2, self.routes()[h2].index(p2))

            self.ImprovePath(h1)
            self.ImprovePath(h2)

            self.update_waste_add(points=[p1, p2], h=[h1, h2])

            self.update_waste_swap(h=[h1, h2])

            i += 1
            improvement = True
            #improvement = True
            print(self.waste_collected() - inc_waste)
            #if self.waste_collected() - inc_waste < 0.01:
            #    break
            print(self.waste_collected())

        if improvement:
            self.tabu.update(self.routes())

            #self.update_waste_add(points=[p1, p2], h=[h1, h2])
            #self.update_waste_swap(h=[h1, h2])




class NeighborhoodChange:

    def change_random(self):
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



    def change_best(self):
        self.calculate_waste_change()

        while not self.waste_change.empty:
            current_waste = self.waste_collected()
            print(current_waste)
            aux = self.waste_change[self.waste_change['total_waste'] == self.waste_change['total_waste'].max()]
            aux = aux[aux['total_time'] == aux['total_time'].min()]

            ind = random.choice(aux.index)

            if aux['total_waste'][ind] <= current_waste:
                break

            p1 = aux['p1'][ind]
            h = aux['h'][ind]
            p2 = aux['p2'][ind]


            self.change_point(p2, h, self.routes()[h].index(p1))
            self.ImprovePath(h)
            #self.update_route(h, self.ImprovePath(self.routes()[h], alpha=10))
            #self.refine()
            self.tabu.update(self.routes())


            self.update_waste_add(points=[p1, p2],h=[h])
            self.update_waste_swap(h=[h])

            self.calculate_waste_change()

        # points = [p for p, h_aux in self.points_h_available().items() if h not in h_aux]
        #
        #
        # for p in points:
        #     self.waste_add = self.waste_add[self.waste_add['point'] != p]
        #     self.waste_add = self.waste_add.append(self.calculate_waste_add2(p))
        #
        # self.waste_add = self.waste_add[self.waste_add['waste'] >= 0]
        # self.waste_add.sort_values(by=['waste'], inplace=True, ascending=False)
        # self.waste_add = self.waste_add.reset_index(drop=True)
        #
        # self.update_time_add()

        #while self.time_add.empty and not self.waste_add.empty:
         #   self.waste_add = self.waste_add[self.waste_add['waste'] != max(self.waste_add['waste'])]
          #  self.update_time_add()




