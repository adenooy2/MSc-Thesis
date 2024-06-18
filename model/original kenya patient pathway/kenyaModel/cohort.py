from person import person
import numpy as np
from collections import Counter

class cohort():

    def __init__(self):
        self.pop = []
        self.pop_size=0

    def add_person(self,per):
        self.pop.append(per)
        self.pop_size=self.pop_size+1

    def get_person(self,ind):
         return self.pop[ind]

    def populate_cohort(self, N):
        self.pop = [person() for i in range(N)]  # our population
        self.pop_size = N

