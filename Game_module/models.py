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

# Assigning Treatment variables

# turn_treatment = itertools.cycle(['baseline', 'black-box', 'partial', 'full', 'performance'])
GROUPS = ['full', 'partial', 'partialc', 'black-box', 'baseline']



def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


class Constants(BaseConstants):
    name_in_url = 'Game_module'
    profit_choice = [[-1, "Less than 0 E$"],
                     [0, "Between 0 E$ and 1,999 E$"],
                     [1, "Between 2,000 E$ and 3,999 E$"],
                     [2, "Between 4,000 E$ and 5,999 E$"],
                     [3, "Between 6,000 E$ and 7,999 E$"],
                     [4, "Between 8,000 E$ and 9,999 E$"],
                     [5, "More than 10,000 E$"]]
    players_per_group = None
    num_rounds = 45
    timer_text = 'Time to complete the simulation (min:sec):'
    instructions_template_a2 = 'Game_module/z_instructions_after_2.html'
    treatment_hidden = 'Game_module/z_Treatment_hidden.html'
    treatment_uncensored = 'Game_module/z_Treatment_uncensored.html'
    sale_price = 4
    cost = 2
    gamma = 0.25
    max_demand = 600
    base_pay = 3
    wait_e1 = 20
    wait_e2 = 40
    wait_game = 0
    wait_game_result = 0
    wait_every5 = 0


class Subsession(BaseSubsession):
    def creating_session(self):

        self.session.vars['completion_by_treatment'] = {color: 0 for color in GROUPS}
        import time
        for p in self.get_players():
            p.participant.vars['expiry'] = time.time() + self.session.config['allocated_time_min'] * 60

        demand_type = str('demand_') + self.session.config['demand_type'] + str(".csv")
        ifile = open(demand_type, 'rt')
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
        self.session.vars['ai_counterfact_rec'] = [70, 93, 40, 54, 66, 76, 85, 61, 68, 75, 81, 87, 71, 56, 61, 65, 69,
                                                   73, 77, 66, 56, 59, 50, 53, 56]


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    treatment = models.StringField()
    ai_trust = models.IntegerField(blank=True, min=0, max=10, label="How much do you trust BakerAI's recommendations?")
    demand = models.PositiveIntegerField()
    orderquantity = models.PositiveIntegerField(min=0, max=800)
    orderquantity2 = models.PositiveIntegerField(min=0, max=800)
    sales = models.PositiveIntegerField()
    cost = models.PositiveIntegerField()
    revenue = models.PositiveIntegerField()
    leftover = models.PositiveIntegerField()
    profit = models.CurrencyField()
    cum_profit = models.CurrencyField()
    ai_recommend = models.PositiveIntegerField()
    ai_profit = models.CurrencyField(initial=0)
    ai_profit_round = models.CurrencyField(initial=0)
    ai_profit_cum = models.CurrencyField(initial=0)
    answer_true = models.BooleanField(initial=False)
    profit_true = models.BooleanField(initial=False)
    correct_answers = models.IntegerField(initial=0)
    demand_quantity_dif = models.IntegerField()


    hidden_ai = models.BooleanField()
    # submit_ai = models.PositiveIntegerField(default=0, min=0, max=1)
    keep_q = models.PositiveIntegerField(default=0, min=0, max=300)
    # ai_click = models.PositiveIntegerField(default=0)

    treatment_test1 = models.BooleanField(label="- For the next day, BakerAI would recommend ...",
                                          choices=[
                                              [False, 'More than 80 loaves'],
                                              [True, 'Less than 80 loaves']
                                          ], widget=widgets.RadioSelect)
    treatment_test2 = models.BooleanField(label="- For the next day, BakerAI would recommend ...",
                                          choices=[
                                              [True, 'More than 220 loaves'],
                                              [False, 'Less than 220 loaves']
                                          ], widget=widgets.RadioSelect)

    attention_model_sale = models.IntegerField(
        label="How much do your customers pay for a loaf of bread? (Unit selling price)",
        choices=[[1, "1 E$"], [2, "2 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"]],
        widget=widgets.RadioSelectHorizontal)

    attention_demand = models.IntegerField(
        label="What is the maximum demand observed historically? (Mentioned in the instructions)",
        choices=[[100, "100"],
                 [200, "200"],
                 [300, "300"],
                 [400, "400"],
                 [500, "500"],
                 [600, "600"],
                 [700, "700"]], widget=widgets.RadioSelectHorizontal)

    attention_loss = models.IntegerField(
        label="How many experimental dollars (E$) do you lose for each unsold loaf of bread?",
        choices=[[1, "1 E$"], [2, "2 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"]],
        widget=widgets.RadioSelectHorizontal)

    attention_profit = models.IntegerField(label="What is your current cumulative profit?",
                                           choices=Constants.profit_choice, widget=widgets.RadioSelect)
    attention_model_cost = models.IntegerField(label="How much do you pay for a loaf of bread? (Unit purchase cost) ",
                                               choices=[[1, "1 E$"], [2, "2 E$"], [3, "3 E$"], [4, "4 E$"], [7, "7 E$"]]
                                               , widget=widgets.RadioSelectHorizontal)
    ai_text = models.StringField()
    error1_count = models.IntegerField(default=0, initial=0)
    error2_count = models.IntegerField(default=0, initial=0)

    def treatment_test1_error_message(self, value):
        if not value:
            self.error1_count = self.error1_count + 1
            return "The correct answer should be less than 80 loaves. The reason is that you ordered too many " \
                   "loaves on Day 2. You had to throw 50 unsold loaves away."

    def treatment_test2_error_message(self, value):
        if not value:
            self.error2_count = self.error2_count + 1
            return "The correct answer should be more than 220 loaves. " \
                   "The reason is that you did not order enough on Day 5. There might be some other " \
                   "customers you could not serve."


def custom_export(players):
    # header row
    yield ['session', 'participant_code', 'round_number', 'demand', 'quantity',
           'sales', 'orderquantity2', 'cost',
           'leftover', 'ai_rec', 'profit', 'ai_profit_cum', 'id_in_group', 'payoff',
           'ai_hidden', 'correct answers', 'profit_true', 'answer_true']
    for p in players:
        participant = p.participant
        yield [p.session.code, p.participant.code, p.round_number, p.demand,
               p.orderquantity, p.sales, p.orderquantity2,
               p.cost, p.leftover, p.ai_recommend, p.profit, p.ai_profit_cum,
               p.id_in_group, p.payoff, p.hidden_ai, p.correct_answers, p.profit_true, p.answer_true]
