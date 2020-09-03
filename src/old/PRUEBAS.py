from src.WasteCollection import WasteCollection
from src.Route import Route, RouteCollection


waste_collection = WasteCollection(
    file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
    file_times="data/times-between-pickup-points.txt"
)

collection = RouteCollection(waste_collection,
                             orig=5,
                             dest=5,
                             horizon=7
                             )


n = Neighborhood(collection)

n.tabu_p_h(2045,2)
n.tabu_list = {2045: [0,3,5]}
n.tabu_p_h(2045,2)
n.tabu_p_h(2045,3)
a = 3 in n.tabu_list[2045]

3 in n.tabu_list[2045]
2045 in n.tabu_list.keys()
n.points_h_available()
n.waste_add()

a = n.add_best_neighbors()
a[0].routes()
len(a)
collection.h_without_point(2045)
collection = a[0]
n.collection = n.add_best_neighbors()[0]
n.collection.routes()
n.swap_best_neighbors().routes()

n = Neighborhood(collection)
n.collection = n.add_best_neighbors()
n.collection.routes()
n.collection = n.random_swap_point()
n.collection.total_time()
a = n.change_best_neighbors()
a.routes()

n.collection.total_time()
n.random_change_point().total_time()
n.collection.routes()
a = n.remove_best_neighbors()
n.collection.total_time()
a.total_time()
a.waste_collected()
n.collection.waste_collected()
n.random_remove().routes()

collection = vns.best_collection
collection = vns.collection
vns.neighborhood.collection = vns.neighborhood.random_remove()
vns.collection = vns.neighborhood.collection
vns = VNS(collection)
vns.GVNS(2,2,3)
vns.collection. \
    routes()
n.waste_add.reset_index()
vns.best_collection.waste_collected()
vns.remove_best_neighbors().waste_collected()
vns.print(collection)
point = 2045
best = vns.collection
vns.tabu_list[2045]
vns.add_tabu({p: list(range(best.horizon)) for p in best.waste_collection.pickup_points if p != point})
a[2045]
vns.tabu_list = {}
vns.points_h_available()
vns.update_tabu_list()

import json


x = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
}

x = {
    "iter": 2,
    "waste_collected": 150,
    "total_time": 125,
    "time": 10,
    "neighborhood": "add",
    "route": [[int(r2) for r2 in r] for r in vns.collection.routes()]
}

print(json.dumps(x))


x = {
  "name": "John",
  "age": 30,
  "married": True,
  "divorced": False,
  "children": ("Ann","Billy"),
  "pets": None,
  "cars": [
    {"model": "BMW 230", "mpg": 27.5},
    {"model": "Ford Edge", "mpg": 24.1}
  ]
}

print(json.dumps(x))

f = open("data.txt", "r")
json.loads(f.read())

l = []
with open('data.txt') as json_file:
    for cnt, line in enumerate(json_file):
        l.append(json.loads(line))
