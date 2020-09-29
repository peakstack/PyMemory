import json
import os


class PlayerStatistics:
    def __init__(self):
        self.data = {}
        self.save_file = 'stats.json'

    def update_player(self, name, ratio):
        if not self.data.__contains__(name):
            self.data[name] = 0
            self.save_to_file()

        if ratio > self.data[name]:
            self.data[name] = ratio
            self.save_to_file()

    def is_new_highscore(self, name, ratio):
        try:
            return ratio > self.data[name]
        except KeyError:
            return True

    def save_to_file(self):
        with open(self.save_file, 'w') as outfile:
            json.dump(self.data, outfile)

    def load_from_file(self):
        if not os.path.exists(self.save_file):
            open(self.save_file, 'w').close()
            self.save_to_file()

        with open(self.save_file) as file:
            self.data = json.load(file)

    def get_highscore(self, name):
        try:
            return self.data[name]
        except KeyError:
            return None
