import csv

from otree.api import (
    models,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
)

author = 'Onur'

doc = """
Demo before AI
"""


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


class Constants(BaseConstants):
    name_in_url = 'Demo_module'
    num_rounds = 3
    #timer_text = 'Time to complete the simulation (min:sec):'
    players_per_group = None
    payment_per_correct_answer = 2
    instructions_template = 'Demo_module_wo_AI/z_instructions_new.html'
    sale_price = 4
    cost = 3
    gamma = 0.25
    max_demand = 300
    wait_game = 0


class Subsession(BaseSubsession):
    def creating_session(self):
        ifile = open('randomdemand.csv', 'rt')
        dema = []
        try:
            reader = csv.reader(ifile)
            for row in reader:
                dema.append(list(map(int, row)))
        finally:
            ifile.close()

        his_file = open('historydemand.csv', 'rt')
        history_demand = []
        try:
            reader = csv.reader(his_file)
            for row in reader:
                history_demand.append(list(map(int, row)))
        finally:
            ifile.close()

        # Demand inputs
        self.session.vars['demand'] = dema[0]
        self.session.vars['historydemand'] = history_demand[0]
        hist_dem = [223, 300, 18, 169, 151, 237, 101]
        self.session.vars['demo_demand'] = hist_dem[-Constants.num_rounds:]

        # Assigning Treatment variables
        #import itertools
        #turn_treatment = itertools.cycle([True, False])
        #for player in self.get_players():
        #    player.treatment = next(turn_treatment)


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.BooleanField()

    demand = models.PositiveIntegerField()
    orderquantity = models.PositiveIntegerField(min=0, max=400)
    sales = models.PositiveIntegerField()
    revenue = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()
    leftover = models.PositiveIntegerField()
    profit = models.IntegerField()

    def orderquantity_error_message(self, value):
        if value == int():
            return "Please enter your order quantity"
    pass


