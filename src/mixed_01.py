from VNS2 import VNS
from WasteCollection import WasteCollection
from Route import Route, RouteCollection

w_mixed = WasteCollection(file_filling_rates="data/pickup-point-filling-rates-mixed.csv",
                          file_times="data/times-between-pickup-points.txt")

collection_mixed = RouteCollection(w_mixed,
                                   orig=5,
                                   dest=5,
                                   horizon=5,
                                   max_tabu=0
                                   )

opt_mixed = VNS(collection_mixed, path='results/mixed_01')
opt_mixed.GVNS(2,2,1)