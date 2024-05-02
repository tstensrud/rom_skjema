class Room():
    def __init__(self, area: float, room_population: int, air_per_person: float,
                 air_emissions: float, air_process: float, air_minimum: float, regular_ventilasjon: bool,
                 displacement_ventilation: bool, heat_exchange: str, vav: bool, cav: bool, temp: bool, co2: bool,
                 movement: bool, moisture: bool, time: bool, notes: str, activity: str,  db_teknisk: int,
                 db_rw_naborom: int, db_rw_korridor: int, additional: str):

        self.area: float = area
        self.room_population: int = room_population
        self.air_per_person: float = air_per_person
        self.air_emission: float = air_emissions
        self.air_process: float = air_process
        self.air_minimum: float = air_minimum
        self.regular_ventilation: bool = regular_ventilasjon
        self.displacement_ventilation: bool = displacement_ventilation
        self.heat_exchange: str = heat_exchange
        self.room_control = {
            "vav": vav,
            "cav": cav,
            "temp": temp,
            "co2": co2,
            "movement": movement,
            "moisture": moisture,
            "time": time
        }
        self.notes: str = notes
        self.activity: str = activity
        self.sound = {
            "db_teknisk": db_teknisk,
            "db_rw_naborom": db_rw_naborom,
            "db_rw_korridor": db_rw_korridor
        }
        self.additional: str = additional

        self.chosen_air_supply: float = 0
        self.chosen_air_exhaust = 0
        self.system: str = ""


    def get_required_air(self) -> float:
        room_required_persons = self.room_population * self.air_per_person
        room_required_emissions = self.area * self.air_emission
        room_requirement = room_required_persons + room_required_emissions + self.air_process
        return room_requirement

    def get_minium_air(self) -> float:
        return self.air_minimum * self.area

    def get_air_per_area(self) -> float:
        return self.chosen_air_supply / self.area

class RoomUndervisningsAreal:
    def __init__(self, room_number: str, room_name: str, area: float, population: int):
        self.room_number: str = room_number
        self.room_name: str = room_name
        self.room_area: float = area
        self.room_population: int = population
        self.room = Room(self.room_area,
                         self.room_population,
                        26,
                        7.2,
                        0,
                        3.6,
                        True,
                        False,
                        "R",
                        True,
                        False,
                        True,
                        True,
                        False,
                        False,
                        False,
                        "",
                        "",
                        28,
                        48,
                        34,
                        "")
    def get_room(self):
        return self.room