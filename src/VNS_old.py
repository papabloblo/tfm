import random as random
class VNS:
    def __init__(self):
        self.iter = 0
    def shake(self, k=1):
        points = self.vnd(k)
        intento = True
        while intento:
            add = random.choice([True, False])
            h = random.choice(range(7))
            position = random.choice(range(1, len(self.Solution.route[h]['route'])-1))
            points = [p for p in points if p not in self.Solution.extract_routes(self.Solution.route)[h]]
            point = random.choice(points)
            try:
                if add:
                    new_route = self.Solution.add_point(h, point, position)
                else:
                    new_route = self.Solution.swap_point(h, point, position)
                intento=False
            except:
                0
        return new_route

    def solution(self, sol):
        self.Solution = sol
        self.tabu_points = dict.fromkeys(self.Solution.pickup_points, 0)

    def update_candidates(self):
        points = self.Solution.extract_routes(self.Solution.route)
        points = list(chain(*points, []))
        points = [p for p in points if p not in [self.Solution.orig, self.Solution.dest]]
        tabu_points = dict.fromkeys(self.Solution.pickup_points, 0)
        for p in points:
            tabu_points[p] += 1
        self.tabu_points = tabu_points

    def vnd(self, k):
        tabu2 = self.tabu_points.values()
        tabu2 = list(set(tabu2))
        tabu2.sort()
        tabu2 = tabu2[:k]
        tabu3 = {p: i for p, i in self.tabu_points.items() if i in tabu2}
        tabu3 = list(tabu3.keys())
        return tabu3

    def gvns(self, k_max = 6, l_max=4, h=[6]):
        k = 0
        ok = False
        while ok is False and k < k_max:
            k += 1
            print("k:", k)
            x = self.shake(k)
            l = 0
            ok2 = False
            while ok2 is False and l < l_max:
                l += 1
                print("l:", l)
                neighbors = self.Solution.neighboorhood2(points=[self.vnd(l)]*7,
                                                        route = x,
                                                         n_indexes=100,
                                                         n_points=None,
                                                         indexes=None,
                                                         h=h,

                                                         # n_points = i
                                                         )
                new_sol = self.Solution.best_neighbor(neighbors, k=1, vecino_bueno=True)
                if len(new_sol) > 0:
                    ok2 = True
                    new_sol = new_sol[0]
            if len(new_sol) > 0:
                ok = True
            else:
                new_sol = self.Solution.route
                print("¡No conseguido!")

        return new_sol

    def optimize(self, n_iter=10, n_indexes=10, n_points=10, indexes=None, print_each=10, h=[6]):
        max_iter = self.iter + n_iter
        for i in range(n_iter):

            self.iter += 1

            start = time.time()

            new_sol = self.gvns(h=h)
            self.update_candidates()
            self.Solution.route = new_sol
            if i%print_each == 0:
                print("Iteración", self.iter, "de", max_iter)
                print(self.tabu_points)


                print("Tiempo medio:", round(self.Solution.total_time()/len(self.Solution.route),2))
                print("Recogida total:", round(self.Solution.total_collect(), 2))
                print("Puntos de recogida", [len(r['route']) for r in self.Solution.route])

                print("\n")

vns = VNS()
vns.solution(mi)
vns.optimize(print_each=1, n_iter = 5, h=list(
                                                             np.random.choice(range(0, 7),
                                                                              size=random.choice(range(1, 8)),
                                                                              replace=False
                                                                              )
                                                         ))

vns.optimize(print_each=1, n_iter = 5, h=[6])
vns.gvns()
vns.shake()
vns.tabu_points
vns.update_candidates()
len(vns.vnd(1))
len(vns.vnd(2))
len(vns.vnd(3))
len(vns.vnd(4))
len(vns.vnd(5))
len(vns.vnd(6))
len(vns.vnd(7))