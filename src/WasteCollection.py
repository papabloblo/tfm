import csv
import math
import random

class WasteCollection:
    def __init__(self, file_filling_rates, file_times, ini_points=None, random_fill_ini=False, collection_time=90):
        if ini_points is None:
            self.ini_points = [0, 5, 15]
        else:
            self.ini_points = ini_points

        self.collection_time = collection_time

        filling_rates = self.read_filling_rates(file_filling_rates)
        self.fill_rate = filling_rates['fill_rate']
        if random_fill_ini:
            self.fill_ini = {p: random.random() for p in filling_rates['fill_ini'].keys()}
        else:
            self.fill_ini = filling_rates['fill_ini']

        self.times = self.read_times(file_times)
        self.pickup_points = self.extract_pickup_points()

    def read_times(self, file_times):
        """
        Read times between pickup points and add the collection time.
        :param file_times: string with route file
        :return: dictionary
        """
        times = {}
        with open(file_times) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')

            line_count = 0
            for row in csv_reader:
                if line_count > 0:

                    orig = int(row[0])
                    dest = int(row[1])
                    t = float(row[2])

                    if dest not in self.ini_points:
                        t += self.collection_time

                    if orig not in times.keys():
                        times[orig] = {dest: t}
                    else:
                        times[orig][dest] = t

                line_count += 1

        for p in times.keys():
            times[p][p] = 0

        return times

    def read_filling_rates(self, file_filling_rates):
        fill_rate = {}
        fill_ini = {}
        with open(file_filling_rates) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')

            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    try:
                        fill_rate[int(row[0])] = float(row[9])
                        fill_ini[int(row[0])] = float(row[8])/100
                    except:
                        print('Punto', int(row[0]))
                        print(row, '\n')
                line_count += 1

        for p in self.ini_points:
            fill_rate[p] = 0
            fill_ini[p] = 0

        return {'fill_rate': fill_rate, 'fill_ini': fill_ini}

    def extract_pickup_points(self):
        points = [p for p in self.fill_rate.keys() if p not in self.ini_points]
        points = [p for p in points if p in self.times.keys()]
        return points

    def time_points(self, orig, dest):
        return self.times[orig][dest]

    def overflowing_day(self, point):
        """
        Calculate the first overflowing day
        :param point: integer.
        :return: integer. A integer between 0 and the horizon (default horizon=5).
        """
        return math.ceil((1 - self.fill_ini[point])/self.fill_rate[point])

    def real_fill_level(self, point, h):
        # DUDA: ¿el nivel del día 0 es fill ini o fill ini + fill_rate?
        # Resuelto: fill ini + fill_rate -> párrafo debajo de ecuación 4
        return self.fill_ini[point] + self.fill_rate[point]*h

    def fill_level(self, point, days, fill_ini=None):
        if fill_ini is None:
            fill_ini = 0
        fill = min(1, fill_ini + self.fill_rate[point]*days)
        return fill

    def waste_by_h(self, point, H):
        waste_h = {}
        for i, h in enumerate(H):
            if i == 0:
                dif_h = h
                waste = self.fill_rate[point] * dif_h + self.fill_ini[point]
            else:
                dif_h = h-H[i-1]
                waste = self.fill_rate[point] * dif_h

            waste_h[h] = min(1, waste)
        return waste_h

    def waste_by_point(self, point, H):
        return sum(self.waste_by_h(point, H).values())

    def calculate_route_time(self, route):
        route_time = 0
        for i, p in enumerate(route[:-1]):
            route_time += self.time_points(p, route[i + 1])
        return route_time

    def min_time_point(self, point_orig, points_dest=None):
        if points_dest == None:
            points_dest = self.pickup_points
        times = self.times[point_orig]
        times = [t for p, t in times.items() if p in points_dest]
        return min(times)


