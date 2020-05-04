class Tabu:
    def __init__(self):
        self.tabu_list = {}
        self.max_tabu = 50

    def clean_empty(self):
        tabu_list2 = self.tabu_list.copy()
        for p in self.tabu_list.keys():
            if len(self.tabu_list[p]) == 0:
                del tabu_list2[p]
        self.tabu_list = tabu_list2.copy()
    def add_tabu(self, p_h, ini_tabu=1):
        for p, h in p_h.items():
            if p not in self.tabu_list.keys():
                self.tabu_list[p] = dict.fromkeys(h, ini_tabu)
            else:
                for h2 in h:
                    self.tabu_list[p][h2] = ini_tabu

    def update_tabu_list(self):
        for p in self.tabu_list.keys():
            self.tabu_list[p] = {h: i + 1 for h, i in self.tabu_list[p].items() if i + 1 <= self.max_tabu}
        self.clean_empty()

    def delete(self, p_h):
        for p, h in p_h.items():
            for h2 in h:
                del self.tabu_list[p][h2]
        self.clean_empty()

    def delete_h(self, h):
        for p in self.tabu_list.keys():
            self.tabu_list[p] = {h2: i for h2, i in self.tabu_list[p].items() if h2 not in h}
        self.clean_empty()


    def tabu(self):
        return {p: list(h.keys()) for p, h in self.tabu_list.items()}

