import csv

from otree.api import (
    models,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    widgets
)

author = 'Onur'

doc = """
Actual Simulation
"""


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


class Constants(BaseConstants):
    name_in_url = 'Game_module_wo_AI'
    gender = ["Female", "Male", "Other", "Prefer Not to Say"]
    education = ["No Degree", "School to a Certain Extent", "High School", "Associate Degree",
                 "Bachelor's degree", "Master's Degree", "Professional Degree", "Doctorate Degree", "Prefer Not to Say"]
    players_per_group = None
    num_rounds = 30
    # timer_text = 'Time to complete the simulation (min:sec):'
    instructions_template_a2 = 'Game_module_wo_AI/z_instructions_after_2.html'
    sale_price = 4
    cost = 3
    gamma = 0.25
    max_demand = 300
    base_pay = 3
    wait = 1
    wait_game = 0
    wait_game_result = 0
    wait_every5 = 0


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

        # Assigning Treatment variables
        # import itertools
        # turn_treatment = itertools.cycle([True, False])
        # for player in self.get_players():
        #    player.treatment = next(turn_treatment)


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    def live_oq(self, data):
        print(data)
        if len(data) != 0 and data['orderquantity1'] != '':
            x = int(data['orderquantity1'])
            self.order_wip = x
            if data['orderquantity2'] != 0 and data['orderquantity2'] != '':
                self.orderquantity2 = int(data['orderquantity2'])
        return {self.id_in_group: data}

    demand = models.PositiveIntegerField()
    orderquantity = models.PositiveIntegerField(min=0, max=500)
    sales = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()
    revenue = models.PositiveIntegerField()
    leftover = models.PositiveIntegerField()
    profit = models.CurrencyField()

    comment = models.LongStringField(blank=True, label="If you have any feedback, you can type it in the box below")

    answer_true = models.BooleanField(initial=False)
    profit_true = models.BooleanField(initial=False)

    hidden_ai = models.BooleanField()

    treatment_test1 = models.BooleanField(label="- For the next day, the A.I. would order ...",
                                          choices=[
                                              [False, 'More than 80 loaves'],
                                              [True, 'Less than 80 loaves']
                                          ], widget=widgets.RadioSelect)
    treatment_test2 = models.BooleanField(label="- For the next day, the A.I. would order ...",
                                          choices=[
                                              [True, 'More than 220 loaves'],
                                              [False, 'Less than 220 loaves']
                                          ], widget=widgets.RadioSelect)

    age = models.PositiveIntegerField(label="What is your age?", min=18, blank=True)
    gender = models.StringField(label=" Which of the following most accurately describes you?",
                                choices=Constants.gender, blank=True)
    education = models.StringField(label="What is the highest degree or level of school you have completed?",
                                   choices=Constants.education, blank=True)

    attention_model_sale = models.IntegerField(
        label="How much do your customers pay for a loaf of bread? (Unit selling price)",
        choices=[[1, "1 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"], [10, "10 E$"]],
        widget=widgets.RadioSelectHorizontal)

    attention_demand = models.IntegerField(
        label="What is the maximum demand observed historically? (Mentioned in the instructions)",
        choices=[[100, "100"],
                 [200, "200"],
                 [300, "300"],
                 [400, "400"],
                 [500, "500"],
                 [600, "600"],
                 [700, "700"],
                 [0, "I don't know"]], widget=widgets.RadioSelectHorizontal)

    attention_loss = models.IntegerField(
        label="How many experimental dollars (E$) do you lose for each unsold loaf of bread?",
        choices=[[1, "1 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"], [10, "10 E$"]],
        widget=widgets.RadioSelectHorizontal)

    attention_profit = models.IntegerField(label="What is your current cumulative profit?",
                                           choices=[[-1, "Less than 0 E$"],
                                                    [0, "Between 0 E$ and 200 E$"],
                                                    [1, "Between 201 E$ and 400 E$"],
                                                    [2, "Between 401 E$ and 600 E$"],
                                                    [3, "Between 601 E$ and 800 E$"],
                                                    [4, "Between 801 E$ and 1000 E$"],
                                                    [5, "More than 1000 E$"],
                                                    [-2, "I don't remember"]], widget=widgets.RadioSelect)
    attention_model_cost = models.IntegerField(label="How much do you pay for a loaf of bread? (Unit purchase cost) ",
                                               choices=[[1, "1 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"],
                                                        [10, "10 E$"]]
                                               , widget=widgets.RadioSelectHorizontal)

    def treatment_test1_error_message(self, value):
        if not value:
            return "The correct answer should be less than 80 loaves. The reason is that you ordered too many " \
                   "loaves on Day 2. You had to throw 50 unsold loaves away."

    def treatment_test2_error_message(self, value):
        if not value:
            return "The correct answer should be more than 220 loaves. " \
                   "The reason is that you did not order enough on Day 5."


def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'round_number', 'demand', 'quantity',
           'sales', 'cost',
           'leftover', 'profit', 'id_in_group', 'payoff', 'attention profit', 'attention sale', 'attention cost',
           'attention loss', 'attention_demand', 'ans_true', 'ans_profit']
    for p in players:
        yield [p.session.code, p.participant.code, p.round_number, p.demand,
               p.orderquantity, p.sales,
               p.cost, p.leftover, p.profit,
               p.id_in_group, p.payoff, p.attention_profit, p.attention_model_sale, p.attention_model_cost,
               p.attention_loss, p.attention_demand, p.answer_true, p.profit_true]
