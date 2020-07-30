import os
import argparse
import json

def createFolderResults(path):
    os.mkdir(path)

def configFile(id, waste, orig, dest, horizon, tabu, epsilon):
    x = {
        'id': id,
        'waste': waste,
        'orig': orig,
        'dest': dest,
        'horizon': horizon,
        'tabu': tabu,
        'epsilon': epsilon
    }
    f = open(path+"/config.json", "a")
    f.write(json.dumps(x) + '\n')
    f.close()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument("id", type=str,
                        help="type")

    parser.add_argument("waste", type=str,
                        help="waste")

    parser.add_argument("orig", type=int,
                        help="Origin")

    parser.add_argument("dest",  type=int,
                        help="Destination")

    parser.add_argument("horizon",  type=int,
                        help="Horizon")

    parser.add_argument("tabu", type=int,
                        help="tabu")

    parser.add_argument("epsilon", type=bool,
                        help="blah")

    args = parser.parse_args()

    path = 'results/' + args.id
    createFolderResults(path)

    configFile(
        args.id,
        args.waste,

        args.orig,
        args.dest,

        args.horizon,
        args.tabu,
        args.epsilon
    )