class RoomUndervisningsAreal:
    def __init__(self, name: str, area: float, room_number: str):
        self.room_number = room_number
        self.name = name
        self.area = area
        self.air_person = 26
        self.air_emission = 7.2
        self.air_process = 0
        self.air_minimum = 3.6
        self.regular = True
        self.displacement = False
        self.heat_exchange = "R"
        self.room_control = {
            "vav": True,
            "cav": False,
            "temp": True,
            "co2": True,
            "movement": False,
            "moisture": False,
            "time": False
        }
        self.notes = ""
        self.activity = ""
        self.sound = {
            "teknisk": 28,
            "rw_naborom": 48,
            "rw_korridor": 34
        }
        self.additional = ""


