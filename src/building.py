class Building:
    def __init__(self, name: str, floors: int):
        self.name: str = name
        self.floors = []
        self.total_floors = floors

    def generate_floors(self):
        for i in range(self.total_floors):
            new_floor = Floor()
            self.floors.append(new_floor)


class Floor:
    def __init__(self):
        self.rooms = []