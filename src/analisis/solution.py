import json
#from src.WasteCollection import WasteCollection
#from src.Route import Route, RouteCollection
from statistics import mean, stdev
import glob
import numpy as np

def read_results(file):
    """
        Lectura del archivo json con los resultados
        de una ejecución.
        Devuelve una lista con un diccionario
        para cada iteración.
    :param file:
    :return:
    """
    result = []
    with open(file) as f:
        line = f.readline()
        while line:
            result.append(json.loads(line))
            line = f.readline()
    return result

def best_solution(results):
    last_iter = len(results) - 1

    if results[last_iter]['best_waste'] > results[last_iter]['candidate1_waste']:
        solution = results[last_iter]['best']
    else:
        solution = results[last_iter]['candidate']
    return solution

def read_config(file):
    with open(file) as f:
        config = json.load(f)
    return config

def waste(waste_type):
    return WasteCollection(
        file_filling_rates="data/pickup-point-filling-rates-" + waste_type + ".csv",
        file_times="data/times-between-pickup-points.txt"
    )

def collection(config, waste_collection, routes):
    return RouteCollection(waste_collection,
                           orig=config['orig'],
                           dest=config['dest'],
                           horizon=config['horizon'],
                           max_tabu=config['tabu'],
                           routes=routes
                           )


def waste_accumulated(p, route_collection):
    fill_rate = route_collection.waste_collection.fill_rate[p]
    fill_ini = route_collection.waste_collection.fill_ini[p]

    collection_days = route_collection.h_with_point(p)

    waste = [fill_ini]
    for h in route_collection.H():
        if h in collection_days:
            waste.append(0)
        else:
            waste.append(fill_rate + waste[-1])

    return waste[1:]

def waste_accumulated_by_h(route_collection):
    pickup_points = route_collection.waste_collection.pickup_points
    waste_accumulated_by_p = {p: waste_accumulated(p, route_collection) for p in pickup_points}

    waste_accumulated_h = []
    for h in route_collection.H():
        waste_accumulated_h.append([w[h] for w in waste_accumulated_by_p.values()])
    return waste_accumulated_h

def overflowing_by_h(route_collection):
    waste = waste_accumulated_by_h(route_collection)
    overflowing = []
    for h in route_collection.H():
        overflowing.append(len([w for w in waste[h] if w > 1]))
    return overflowing



def kpi_by_h(h, route_collection):
    ind = {}

    ind['points_visited'] = len(route_collection.routes()[h])

    ind['waste_collected'] = []
    for p in route_collection.routes()[h]:
        waste_collected = route_collection.waste_collected_point_h2(p, route_collection.h_with_point(p))
        if h in waste_collected.keys():
            ind['waste_collected'].append(waste_collected[h])
    ind['waste_collected'] = sum(ind['waste_collected'])

    ind['total_time'] = route_collection.time_h()[h]/3600

    ind['overflowing'] = overflowing_by_h(route_collection)[h]

    ind['mean_fill_level'] = mean(waste_accumulated_by_h(route_collection)[h])

    return ind

def kpi_total(ind, waste_collection, route_collection):
    total_ind = {'points_visited': 0,
           'waste_collected': 0,
           'total_time': 0,
           'total_distance': 0,
           'overflowing': 0,
           'perc_wasted_collected': 0
           }

    for h in route_collection.H():
        total_ind['points_visited'] += ind[h]['points_visited']
        total_ind['waste_collected'] += ind[h]['waste_collected']
        total_ind['total_time'] += ind[h]['total_time']
        total_ind['overflowing'] += ind[h]['overflowing']

    total_ind['mean_fill_level'] = mean([d['mean_fill_level'] for d in ind])*100

    wasted_generated_by_point = {p: waste_collection.fill_rate[p] * route_collection.horizon + waste_collection.fill_rate[p] for p in waste_collection.pickup_points}
    max_waste = sum(wasted_generated_by_point.values())
    total_ind['perc_wasted_collected'] = route_collection.waste_collected()/max_waste*100

    return total_ind


#TODO: distancia recorrida -> No tengo el archivo (aunque se puede extraer de los tropecientos json)



import pandas as pd

import pickle
scenarios = glob.glob("results/*")

def kpi_calculation(directory, read_fill_ini=False):
    files = glob.glob(directory + "/log_*")
    config = read_config(directory + '/config.json')
    waste_collection = waste(config['waste'])

    kpis = []
    for f in files:
        data = read_results(f)

        if read_fill_ini:
            if f[-2] == '1':
                f2 = f[-2:]
            else:
                f2 = f[-1]
            with open(directory + '/fill_ini_' + f2, 'rb') as file_fill_ini:
                waste_collection.fill_ini = pickle.load(file_fill_ini)

        route_collection = collection(config, waste_collection, best_solution(data))
        ind = [kpi_by_h(h, route_collection) for h in route_collection.H()]
        kpis.append(kpi_total(ind, waste_collection, route_collection))

    final = {}
    best_execution = [i['waste_collected'] for i in kpis]
    best_execution = np.argmax(best_execution)

    for k in kpis[best_execution].keys():
        final[k] = [kpis[best_execution][k]]

    for k in kpis[1].keys():
        aux = [i[k] for i in kpis]
        final[k] += [mean(aux), stdev(aux)]

    return final

def print_kpi(file, read_fill_ini=False):
    kpi = kpi_calculation(file, read_fill_ini)
    for i, v in kpi.items():
        print(i + ":")

        print('\tBest:', round(v[0],2))
        print('\tMean:', round(v[1],2))
        print('\tSD:', round(v[2],2))

# PAPER

## Escenario 1:
##  - tabu: 0
##  - epsilon: no

print_kpi('results/paper_tabu0')

## Escenario 2:
##  - tabu: 0
##  - epsilon: sí

print_kpi('results/paper_tabu0_epsilon')



## Escenario 3:
##  - tabu: 50
##  - epsilon: no

print_kpi('results/paper_tabu50')

## Escenario 4:
##  - tabu: 50
##  - epsilon: sí

print_kpi('results/paper_tabu50_epsilon')

a = read_results('results/paper_tabu50_epsilon/log_1')

w = [i['best_waste'] for i in a]
import matplotlib.pyplot as plt

plt.plot([1, 2, 3, 4], [1, 4, 9, 16])
plt.show()



# MIXED

## Escenario 1:
##  - tabu: 0
##  - epsilon: no

print_kpi('results/mixed_tabu0')

## Escenario 2:
##  - tabu: 0
##  - epsilon: sí

print_kpi('results/mixed_tabu0_epsilon')



## Escenario 3:
##  - tabu: 50
##  - epsilon: no

print_kpi('results/mixed_tabu50')

## Escenario 4:
##  - tabu: 50
##  - epsilon: sí

print_kpi('results/mixed_tabu50_epsilon')


# MIXED (random)

## Escenario 1:
##  - tabu: 0
##  - epsilon: no

print_kpi('results/mixed_tabu0_random', read_fill_ini=True)

## Escenario 2:
##  - tabu: 0
##  - epsilon: sí

print_kpi('results/mixed_tabu0_epsilon_random', read_fill_ini=True)



## Escenario 3:
##  - tabu: 50
##  - epsilon: no

print_kpi('results/mixed_tabu50_random', read_fill_ini=True)

## Escenario 4:
##  - tabu: 50
##  - epsilon: sí

print_kpi('results/mixed_tabu50_random', read_fill_ini=True)



# PAPER (random)

## Escenario 1:
##  - tabu: 0
##  - epsilon: no

print_kpi('results/paper_tabu0_random', read_fill_ini=True)

## Escenario 2:
##  - tabu: 0
##  - epsilon: sí

print_kpi('results/paper_tabu0_epsilon_random', read_fill_ini=True)



## Escenario 3:
##  - tabu: 50
##  - epsilon: no

print_kpi('results/paper_tabu50_random', read_fill_ini=True)

## Escenario 4:
##  - tabu: 50
##  - epsilon: sí

print_kpi('results/paper_tabu50_epsilon_random', read_fill_ini=True)

