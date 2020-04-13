import csv

class WasteCollection:
    def __init__(self, file_filling_rates, file_times, ini_points=None):
        if ini_points is None:
            self.ini_points = [0, 5, 15]
        else:
            self.ini_points = ini_points

        self.fill_rate = self.read_filling_rates(file_filling_rates)
        self.times = self.read_times(file_times)
        self.pickup_points = self.extract_pickup_points()
        self.fill_ini = self.fill_rate

    def read_times(self, file_times):
        times = {}
        with open(file_times) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    orig = int(row[0])
                    dest = int(row[1])
                    t = float(row[2])
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
        with open(file_filling_rates) as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            line_count = 0
            for row in csv_reader:
                if line_count > 0:
                    try:
                        fill_rate[int(row[0])] = float(row[9])
                    except:
                        #fill_rate[int(row[0])] = 0.0
                        print('Punto', int(row[0]))
                        print(row, '\n')
                line_count += 1
        for p in self.ini_points:
            fill_rate[p] = 0
        return fill_rate

    def extract_pickup_points(self):
        points = [p for p in self.fill_rate.keys() if p not in self.ini_points]
        points = [p for p in points if p in self.times.keys()]
        return points

    def time_points(self, orig, dest):
        return self.times[orig][dest]

    def fill_level(self, point, days, fill_ini=None):
        if fill_ini is None:
            fill_ini = 0
        fill = min(1, fill_ini + self.fill_rate[point]*days)
        return fill

    def min_time_point(self, point_orig, points_dest=None):
        if points_dest == None:
            points_dest = self.pickup_points
        times = self.times[point_orig]
        times = [t for p, t in times.items() if p in points_dest]
        return min(times)

a[2181]
p = random.choice(waste_collection.pickup_points)
print(p)
fill_r = waste_collection.fill_rate[p]
fill_ini = waste_collection.fill_ini[p]
print((1-fill_ini)/fill_r)
