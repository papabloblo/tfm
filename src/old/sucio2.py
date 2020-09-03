w = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
              file_times="data/times-between-pickup-points.txt")


r = collection.routes()
collection = RouteCollection(w,
                             orig=5,
                             dest=5,
                             horizon=7,
                             routes=[[5,2045,5], [5,5], [5,5], [5,5], [5,5], [5,5],[5,5]]
                             )

collection = RouteCollection(w,
                             orig=5,
                             dest=5,
                             horizon=5,
                             routes=r
                             )


collection = RouteCollection(w,
                             orig=5,
                             dest=5,
                             horizon=5
                             )

solution = Solution(
                    orig=5,
                    dest=5,
                    horizon=7,
                    file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                    file_times="data/times-between-pickup-points.txt"
                    )

for i in range(10):
    collection.add_best()
    print(collection.waste_collected())
    print(collection.time_add)


for i in range(1):
    collection.swap_best()
    print(collection.waste_collected())
    print(collection.waste_swap)

for i in range(1):
    collection.change_best()
    print(collection.waste_collected())

collection.update_waste_add()

collection.update_time_add()

while collection.time_add.empty:
    collection.waste_add = collection.waste_add[collection.waste_add['waste'] != max(collection.waste_add['waste'])]
    collection.update_time_add()


for i in range(100):
    max_w = 1
    points = np.random.choice(solution.WasteCollection.pickup_points, size=10, replace=False)

    h = np.random.choice(range(solution.horizon), size=3, replace=False)
    # h = [range(7)[i%7]]
    # h=[1,2]
    print(h)

    print('Tamaño vecindad:', max_w)
    # h = [0]
    # print(max_w)
    mi = NeighborhoodAdd(solution.RouteCollection)
    neighbors = mi.generate_neighbors(h, points)

    # neighbors = solution.add_point(max_w=max_w, points=points, h=h)
    neighbors = solution.filter_routes_time_constraint(neighbors)

    # neighbors = [random.choice(neighbors)]
    times = [min(r.time_h()) for r in neighbors]
    neighbors = [n for n in neighbors if min(n.time_h()) == min(times)]

    if len(neighbors) == 0:
        print('Change')
        neighbors = solution.change_point(points, h)
        neighbors = solution.filter_routes_time_constraint(neighbors)

        # neighbors = [random.choice(neighbors)]
        times = [min(r.time_h()) for r in neighbors]
        neighbors = [n for n in neighbors if min(n.time_h()) == min(times)]

    if len(neighbors) == 0:
        break

    res = random.choice(neighbors)
    #res = neighbors[0]
    solution.RouteCollection = res
    print('Función objetivo:', res.waste_collected())
    print('Tiempos por día:', res.time_h())
    print('Número de visitas por día:', [len(x) for x in solution.RouteCollection.extract_routes()])
    print("")

83.88710000000002
19, 86, 14, 15, 21, 13, 16]





















mi = solution.RouteCollection


for i in range(10):
    print(solution.RouteCollection.extract_routes())

    a = solution.random_neighbor()

    solution.RouteCollection = a

solution.RouteCollection.waste_collected_point()

solution.RouteCollection.point_visits()

sol
waste_add = solution.waste_add_point_h()
b = a[2045]
max(b.values())
mi = list(b.values())
mi.sort()
var = mi[-3:-1]
max_w = 2

y = list(set([max(i.values()) for i in a.values()]))
y.sort(reverse=True)
y[:1]


a = solution.new_collection([[5,2045,5], [5,5], [5,5], [5,5], [5,5], [5,5],[5,5]])
a.total_time()
a.horizon = 3
solution.RouteCollection.total_time()

a = solution.RouteCollection.horizon
a[2045]

solution.WasteCollection.fill_rate[2046]
ruta = Route(w,
             orig=5,
             dest=5)


ruta.time()
len(ruta.route())

ruta.add_point(2045, 1)
ruta.add_point(2045, 0)
ruta.time()
ruta.route()

ruta.change_point(2046, 1)
ruta.time()
ruta.route()

ruta.calculate_time

ruta.__route

ruta.__miau


collection = RouteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                             file_times="data/times-between-pickup-points.txt",
                             orig=5,
                             dest=5,
                             horizon=7
                             )

collection.collection[0].add_point(2045,0)
collection.collection[0].change_point(2055,1)
collection.collection[0].add_point(2045,0)

collection.collection[0].route()
collection.collection[0].time()

collection.total_time()

collection.update_route(2, [5, 2045, 5])
collection.update_route(6, [5, 2055, 5])
collection.collection[1].time()
collection.collection[0].time()

collection.extract_routes()
collection.point_visits()

collection.waste_collected()
collection.collection[0].fill_level(2055, 6)
points = list(chain(*collection.extract_routes(), []))
visits = {}
for h, r in enumerate(collection.extract_routes()):
    for p in r:
        if p not in visits.keys():
            visits[p] = {'num': 1, 'days': [h]}
        else:
            visits[p]['num'] +=1
            visits[p]['days'].append(h)

collection = Solution(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                             file_times="data/times-between-pickup-points.txt",
                             orig=5,
                             dest=5,
                             horizon=7
                             )

collection.extract_routes()
collection.waste_collected()
collection.new_waste_collected(2065, 3)


r = collection.routes()
collection = RouteCollection(w,
                             orig=5,
                             dest=5,
                             horizon=5
                             )


#collection = opt.best_collection
opt = VNS(collection, path='superman')

opt.GVNS(2,2,2)
opt.best_collection.tabu.tabu_by_h()

###############################

a = {p: opt.best_collection.waste_collected_point_h2(p, opt.best_collection.point_h2(p)) for p in opt.best_collection.unique_points()}
mi = []
for i in a.values():
    mi += list(i.values())
sum(mi)
sum(mi)/len(mi)