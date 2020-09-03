
import pandas

files = ['data/route_0.csv',
         'data/route_1.csv',
         'data/route_2.csv',
         'data/route_3.csv',
         'data/route_4.csv',
         'data/route_5.csv',
         'data/route_6.csv',
         'data/route_7.csv',
         'data/route_8.csv',
         'data/route_9.csv']

def read_route(file):
    df = pandas.read_csv(file,
                         names=['latitude', 'longitude', 'point', 'time', 'time_acum'],
                         header=0)
    return df['point'].to_list()



routes_paper = []
routes_mixed = []
for x in files:
    route = read_route(x)
    if route[0] == 0:
        routes_paper.append(route)
    else:
        routes_mixed.append(route)


[len(r) for r in routes_mixed]
[len(r) for r in routes_paper]

w_mixed = WasteCollection(
        file_filling_rates="data/pickup-point-filling-rates-" + "mixed" + ".csv",
        file_times="data/times-between-pickup-points.txt"
    )
collection_mixed = RouteCollection(w_mixed,
                                   orig=5,
                                   dest=5,
                                   horizon=5,
                                   max_tabu=0,
                                   routes=routes_mixed
                                   )

ind = [kpi_by_h(h, collection_mixed) for h in collection_mixed.H()]
total = kpi_total(ind, w_mixed, collection_mixed)

for i, v in total.items():
    print(i + ":", round(v, 4))


w_paper = WasteCollection(
        file_filling_rates="data/pickup-point-filling-rates-" + "paper" + ".csv",
        file_times="data/times-between-pickup-points.txt"
    )

collection_paper = RouteCollection(w_paper,
                                   orig=0,
                                   dest=15,
                                   horizon=5,
                                   max_tabu=0,
                                   routes=routes_paper
                                   )

ind = [kpi_by_h(h, collection_paper) for h in collection_paper.H()]
total = kpi_total(ind, w_paper, collection_paper)
for i, v in total.items():
    print(i + ":", round(v, 4))


collection_paper.waste_collected()

ind = [kpi_by_h(h, collection_mixed) for h in collection_mixed.H()]
kpi_total(ind)



