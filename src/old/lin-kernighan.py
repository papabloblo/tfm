
a = opt_mixed.best_collection

h = 1
route = a.routes()[h]

edges_route = edges(route)


def edges(route):
    links = []
    for i, p in enumerate(route[:-2]):
        links.append([p, route[i + 1]])
    return links
dist = w_mixed.times

def time(route, dist):
    t = 0
    for i, p in enumerate(route[:-1]):
        t += dist[p][route[i+1]]
    return(t)


def ImprovePath(route, depth=1, R = [], alpha = 2, max_depth=10):
    if depth < alpha:
        for i, p in enumerate(route[:-1]):
            if p in R:
                continue
            new_tour = route[:i+1]
            aux_tour = route[i+1:-1]
            aux_tour.reverse()
            new_tour += aux_tour
            new_tour.append(route[-1])

            if a.time_aux(new_tour) < a.time_aux(route):
                return new_tour
            else:

                new_R = R + [p]
                new_tour = ImprovePath(new_tour, R=new_R, depth=depth+1, alpha=alpha)
                if a.time_aux(new_tour) < a.time_aux(route):
                    return(new_tour)
        return(route)
    else:
        return(route)


R

route = routes[4]

x = route.copy()
for i in range(10):
    print(a.time_aux(x))
    x = ImprovePath(x, depth=1, alpha=3, R=[])


print(a.time_aux(x))
x = ImprovePath(x, depth=1, alpha=5, R=[])
print(a.time_aux(x))
x = ImprovePath(x, depth=1, alpha=5, R=[])
print(a.time_aux(x))
x = ImprovePath(x, depth=1, alpha=5, R=[])
print(a.time_aux(x))





            #print(i)
                if x in R or i == 0:
                    continue
                gain = dist[x][route[i+1]] - dist[last_point][x]
                #print(gain)
                #if gain > 0:
                new_tour = route[:j+1]
                aux_tour = route[i+1:-1]
                aux_tour.reverse()
                new_tour += aux_tour
                new_tour.append(route[-1])
                new_time = time(new_tour, dist)
                print(new_time)
                if new_time < time(route, dist):
                    prin('miii')
                    #return new_tour
                    break
                else:
                    route = ImprovePath(new_tour, dist, depth=depth+1, R = R + [x])
                    break
    else:
        print('adiós')
        gain = float('-inf')
        best_i = None
        for i, x in enumerate(route[:-2]):
            gain_aux = dist[x][route[i + 1]] - dist[last_point][x]
            if gain_aux > gain:
                best_i = i
                gain = gain_aux

        #if gain > 0:
        new_tour = route[:best_i + 1]
        aux_tour = route[best_i + 1:-1]
        aux_tour.reverse()
        new_tour += aux_tour
        new_tour.append(route[-1])
        new_time = time(new_tour, dist)

        if new_time < time(route, dist):
            return new_tour
        else:
            return ImprovePath(new_route, dist, depth=depth+1, R = R + [route[best_i]])
    return(route)


def ImprovePath(route, dist, depth=1, R=[], alpha=2, max_depth=10, orig_time=100):
    last_point = route[-2]
    print(len(route))

    print('adiós')
    gain = float('-inf')
    best_tour = None
    for i, x in enumerate(route[:-2]):
        gain_aux = dist[x][route[i + 1]] - dist[last_point][x]
        if gain_aux > gain:
            best_i = i
            gain = gain_aux

    # if gain > 0:
    new_tour = route[:best_i + 1]
    aux_tour = route[best_i + 1:-1]
    aux_tour.reverse()
    new_tour += aux_tour
    new_tour.append(route[-1])
    new_time = time(new_tour, dist)
    print(depth)
    print(new_time)
    if new_time < orig_time or depth == max_depth:
        return new_tour
    else:
        return ImprovePath(new_tour, dist, depth=depth + 1, R=R + [route[best_i]], orig_time=orig_time)


orig_time = time(route, dist)
ey = ImprovePath(route, dist, alpha=2, max_depth=100, orig_time=orig_time)
time(ey, dist)

time(route, dist)

last_point = route[-2]
for i, x in enumerate(route[:-2]):
    # print(i)
    if x in R or i == 0:
        continue
    gain = dist[x][route[i + 1]] - dist[last_point][x]
    # print(gain)
    # if gain > 0:
    new_tour = route[:i + 1]
    aux_tour = route[i + 1:-1]
    aux_tour.reverse()
    new_tour += aux_tour
    new_tour.append(route[-1])
    new_time = time(new_tour, dist)
    print(new_time)
    if new_time < time(route, dist):
        break

route_aux = route.copy()
j = 0
while j < 20:
    j += 1
    best_time = float('inf')
    best_tour = None
    for i in range(len(route_aux[:-3])):
        x = route_aux[i]
        new_tour = route_aux[:i + 1]
        aux_tour = route_aux[i + 1:-1]
        aux_tour.reverse()
        new_tour += aux_tour
        new_tour.append(route[-1])
        new_time = time(new_tour, dist)
        if new_time < best_time:
            best_time = new_time
            best_tour = new_tour
            route_aux = best_tour

def opt_swap(route, i, k):
    new_route = route[:i]
    route_aux = route[i:k+1]
    route_aux.reverse()
    new_route += route_aux + route[k+1:]
    return(new_route)

h = 1
route = a.routes()[h]

def ImprovePath(route, dist):
    best_distance = a.time_aux(route)
    improvement = False
    while not improvement:
        for i in range(1,len(route)):
            for k in range(i+1, len(route)):
                new_route = opt_swap(route, i, k)
                new_distance = a.time_aux(new_route)
                if new_distance < best_distance:
                    route = new_route
                    best_distance = new_distance
                    improvement = True
                    break
            if improvement:
                break
        if i == len(route) - 1:
            improvement = True
    return route


for h in range(5):
    route = a.routes()[h]
    print(a.time_aux(route))
    route = ImprovePath(route, dist)
    print(a.time_aux(route))

route = [1,2,3,4,5,6,7,8]

opt_swap(route, 3, 6)

def distance(x, y):
    return dist[x][y]


def reverse_segment_if_better(tour, i, j, k):
    """If reversing tour[i:j] would make the tour shorter, then do it."""
    # Given tour [...A-B...C-D...E-F...]
    A, B, C, D, E, F = tour[i-1], tour[i], tour[j-1], tour[j], tour[k-1], tour[k % len(tour)]
    d0 = distance(A, B) + distance(C, D) + distance(E, F)
    d1 = distance(A, C) + distance(B, D) + distance(E, F)
    d2 = distance(A, B) + distance(C, E) + distance(D, F)
    d3 = distance(A, D) + distance(E, B) + distance(C, F)
    d4 = distance(F, B) + distance(C, D) + distance(E, A)

    if d0 > d1:
        tour[i:j] = reversed(tour[i:j])
        return -d0 + d1
    elif d0 > d2:
        tour[j:k] = reversed(tour[j:k])
        return -d0 + d2
    elif d0 > d4:
        tour[i:k] = reversed(tour[i:k])
        return -d0 + d4
    elif d0 > d3:
        tmp = tour[j:k] + tour[i:j]
        tour[i:k] = tmp
        return -d0 + d3
    return 0


def three_opt(tour):
    """Iterative improvement based on 3 exchange."""
    while True:
        delta = 0
        print(delta)
        for (a, b, c) in all_segments(len(tour)):
            delta += reverse_segment_if_better(tour, a, b, c)
            print(delta)
        if delta >= 0:
            break
    return tour

def all_segments(n: int):
    """Generate all segments combinations"""
    return ((i, j, k)
        for i in range(n)
        for j in range(i + 2, n)
        for k in range(j + 2, n + (i > 0)))

route = opt_mixed.candidate_collection.routes()[2].copy()
route = route[:10] + [5]
print(a.time_aux(route))
route2 = three_opt(route.copy())
print(a.time_aux(route2))
