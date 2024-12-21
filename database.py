
import json
import datetime

class DataBase:
    def __init__ (self, path = "notes.json"):
        self.path = path

    def add_note (self, note):
        now = datetime.datetime.now()
        formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
        #print(formatted_time)

        with open(self.path, "r") as file:
            data = json.load(file)

        data[str(formatted_time)] = note

        with open(self.path, "w") as file:

            json.dump(data, file)
        

"""data = DataBase()
data.add_note("hello there")"""