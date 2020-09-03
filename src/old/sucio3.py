
w_mixed = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                          file_times="data/times-between-pickup-points.txt")

w_paper = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-paper.csv",
                          file_times="data/times-between-pickup-points.txt")

w_mixed = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                          file_times="data/times-between-pickup-points.txt")

collection_mixed = RouteCollection(w_mixed,
                                   orig=5,
                                   dest=5,
                                   horizon=5,
                                   max_tabu=0
                                   )

opt_mixed = VNS(collection_mixed, path='mixed')
opt_mixed.GVNS(2,2,50)

collection_mixed.add_best()
collection_mixed.routes()

collection_mixed.add_point(2045, 0, 0)
collection_mixed.add_point(2055, 0, 0)
collection_mixed.add_point(2065, 0, 0)
collection_mixed.collection[0].Improve(inplace=False)

collection_mixed.add_random()
collection_mixed.waste_collected()

#collection_mixed = opt_mixed.candidate_collection
opt_mixed = VNS(collection_mixed, path='mixed')
opt_mixed.epsilon = 0.5
opt_mixed.GVNS(2,2,50)

ay = opt_mixed.best_collection

opt_mixed = VNS(ay, path='mixed')
opt_mixed.GVNS(2,2,50)

collection_paper = RouteCollection(w_paper,
                                   orig=0,
                                   dest=15,
                                   horizon=5,
                                   max_tabu=0
                                   )


opt_mixed = VNS(collection_mixed, path='mixed')
opt_paper = VNS(collection_paper, path='paper', epsilon=True)

opt_mixed.GVNS(2,2,2)
opt_paper.GVNS(2,2,50)

opt_mixed.candidate_collection = opt_mixed.best_collection
opt_mixed.print()

opt_paper.candidate_collection = opt_paper.best_collection
opt_paper.print()

# Swap dentro de una ruta

ruta = opt_paper.best_collection

ruta
a = []

for h in range(ruta.horizon):
    print(h)
    ruta0 = ruta.collection[h]

    ruta_orig = ruta0.route()

    best = ruta_orig.copy()
    best_time = ruta0.time()
    print(best_time)

    mejora = True
    while mejora:
        mejora = False
        ruta_orig = best.copy()
        for i1 in range(1, len(ruta_orig)-1):
            for i2 in range(i1, len(ruta_orig) - 1):
                ruta_aux = ruta_orig.copy()
                ruta_aux[i1] = ruta_orig[i2]
                ruta_aux[i2] = ruta_orig[i1]
                mi = Route(w_paper, 0, 15, ruta_aux)
                if mi.time() < best_time:
                    mejora = True
                    print(mi.time())
                    best = ruta_aux.copy()
                    best_time = mi.time()
    a.append(best)

collection_paper2 = RouteCollection(w_paper,
                                   orig=0,
                                   dest=15,
                                   horizon=5,
                                   max_tabu=25,
                                    routes=a
                                   )

collection_paper2.total_time()
ruta.total_time()

opt_paper = VNS(collection_paper2, path='paper')
opt_paper.GVNS(2,2,2)



col = opt_mixed.candidate_collection


###########################################


a = opt_mixed.candidate_collection

a.waste_add

a.inc_waste(2213, 4)
a.update_waste_add2(2213)

a.waste_add

a.waste_add[a.waste_add['h'] == 0]

points_h_available = a.points_h_available()
b = a.copy()

b.add_point(3620, 0, 15)
print(b.time_h()[0])
b.update_route(0, b.ImprovePath(b.routes()[0], alpha=1, max_depth=900))
print(b.time_h()[0])

b.time_aux(b.routes()[0])
b.time_aux(b.routes()[0])
a.time_aux(a.routes()[0])

b.total_time()
a.total_time()


collection_mixed = RouteCollection(w_mixed,
                                   orig=5,
                                   dest=5,
                                   horizon=5,
                                   max_tabu=100
                                   )

collection_mixed.routes()
for i in range(150):
    collection_mixed.add_random()

collection_mixed.time_h()

collection_mixed = opt_mixed.candidate_collection

opt_mixed.candidate_collection.collection[4].time_by_link()



h = 4
a = opt_mixed.candidate_collection
r = opt_mixed.candidate_collection.routes()[h]

a.time_aux(r)
a.points_h_available()

p = 2046
times = []
for i in range(len(r[:-1])):
    r_aux = r.copy()
    r_aux = r[:i+1] + [p] + r[i+1:]
    times.append(a.time_aux(r_aux))

routes = opt_mixed.candidate_collection.routes()

routes1 = routes.copy()

a.Improve(routes, h=[4])

p = 2046
times = []
times2 = []
for i in range(len(r[:-1])):
    r_aux = [r.copy() for r in routes]
    r_aux[h] = r_aux[h][:i + 1] + [p] + r_aux[h][i + 1:]
    times.append(a.time_aux(r_aux[h]))
    times2.append(a.Improve(r_aux, [h])[h])

a.time_aux(r)
r.reverse()
a.time_aux(r)

r = opt_mixed.candidate_collection.routes()[h]
r_aux = [5]
r.remove(5)
r.remove(5)

while len(r) > 0:
    print(i)
    time = [1/w_mixed.time_points(r_aux[-1], p) for p in r]
    #best_i = np.argmin(time)
    best_i = random.choices(r, weights=time, k=1)[0]
    r_aux.append(best_i)
    r.remove(best_i)

r_aux.append(5)
a.time_aux(r_aux)



i = 0
r_aux = r.copy()
r_aux.remove(5)
r_aux.remove(5)
ay = []
for j in range(4):
    time = {p: w_mixed.time_points(r[i], p) for p in r_aux}
    min_time = min(time.values())
    new = [p for p, t in time.items() if t == min_time][0]
    ay.append(new)
    r_aux.remove(new)







w_mixed = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                          file_times="data/times-between-pickup-points.txt")

w_mixed.calculate_route_time([5,2045, 5])
w_mixed.time_points(2045, 2055)
w_mixed.waste_by_h(2045, [0, 2])
w_mixed.waste_by_point(2045, [0, 2])
w_mixed.fill_rate
w_mixed.fill_ini

r = Route(w_mixed, 5, 5)
r.route
r.add_point(2045,0)
r.add_point(2055,0)
r.add_point(2049,0)
r.add_point(2065,0)
r.time

route = r.route.copy()
for i in range(10):
    route = r.LinKernighan(route, R=[], depth=1, alpha=2)
    print(w_mixed.calculate_route_time(route))


r.time
r.Improve(inplace=False)
r.Improve()
w_mixed.time_points(5, 2045) + w_mixed.time_points(2045, 5)


import json

with open('results/mixed_01/config.json') as f:
    data = json.load(f)

print(data)