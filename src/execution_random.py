from WasteCollection import WasteCollection
from Route import Route, RouteCollection
from VNS import VNS

import pickle
import argparse
import json

def read_configFile(path):
    with open(path + '/config.json') as f:
        data = json.load(f)
    return data

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("path", type=str,
                        help="type")

    parser.add_argument("id", type=str,
                        help="type")

    args = parser.parse_args()


    config = read_configFile(args.path)

    waste_collection = WasteCollection(
        file_filling_rates="data/pickup-point-filling-rates-" + config['waste'] + ".csv",
        file_times="data/times-between-pickup-points.txt",
        random_fill_ini=True
    )

    with open(args.path + '/fill_ini_' + args.id, 'wb') as file_fill_ini:
        pickle.dump(waste_collection.fill_ini, file_fill_ini)

    #with open('results/hola', 'rb') as file_fill_ini:
    #    miau = pickle.load(file_fill_ini)

    collection = RouteCollection(waste_collection,
                                 orig=config['orig'],
                                 dest=config['dest'],
                                 horizon=config['horizon'],
                                 max_tabu=config['tabu']
                                 )

    path = args.path + '/log_' + args.id
    vns = VNS(collection, path, config['epsilon'], config['max_time'])
    vns.GVNS(2, 2, 5000)
