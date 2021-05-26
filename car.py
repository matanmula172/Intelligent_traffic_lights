import math


class Car:
    def __init__(self, arrival_time, id):
        self.arrival_time = arrival_time
        self.id = id

    def get_car_weight(self, current_time):
        return current_time - self.arrival_time + 1

    def get_arrival_time(self):
        return self.arrival_time