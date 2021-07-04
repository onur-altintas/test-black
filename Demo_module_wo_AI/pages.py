from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import random


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


# def ai_rec(sales, orderquantity, round_no, gamma, max_demand, price, cost):
#     epsilon = (gamma * max_demand) / (max(cost, price - cost) * (round_no + 1) ** (1 / 2))
#     if sales == orderquantity:
#         h_t = -(price - cost)
#     else:
#         h_t = cost
#     second_term = orderquantity - epsilon * h_t
#     recommendation = min(max_demand, second_term)
#     return round(recommendation)

def ai_rec(sales, pre_ai, round_no, gamma, max_demand, price, cost):
    epsilon = max_demand / (max(price, cost) * (round_no + 20))
    increase_ht = -(price - cost)
    decrease_ht = cost
    if sales == pre_ai:
        rec = pre_ai - epsilon * increase_ht
    elif sales < pre_ai:
        rec = pre_ai - epsilon * decrease_ht

    return min(max_demand, max(round(rec, 0), 0))


def get_timeout_seconds(player):
    import time
    return player.participant.vars['expiry'] - time.time()


class d_Demo_Intro(Page):
    pass


class e_Demo_Game_w(Page):
    form_model = "player"
    form_fields = ["orderquantity"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def vars_for_template(self):
        hist_dem = self.session.vars['historydemand']
        demand = self.session.vars['demo_demand'][self.round_number - 3]
        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        return {
            'hist_dem': hist_dem,
            'round': self.round_number,
            'demand': demand,
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'demo_rounds': self.session.config['demo_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'total_rounds': self.session.config['ai_fail_rounds']

        }

    def before_next_page(self):
        self.player.demand = self.session.vars['demo_demand'][self.round_number - 3]
        self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity)
        self.player.leftover = self.player.orderquantity - self.player.sales
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity * Constants.cost


class e1_Demo_Results_w(Page):

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def vars_for_template(self):
        demand = self.session.vars['demo_demand'][self.round_number - 1]
        players = self.player.in_all_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        return {
            'round': self.round_number,
            'demand': demand,
            'player_in_all_rounds': players,
            'cum_profit': cum_profit,
            'abs_profit': abs(self.player.profit)
        }

    def before_next_page(self):
        self.participant.vars['pre_profit'] = 0
    # def before_next_page(self):
    #    self.player.round = self.round


page_sequence = [e_Demo_Game_w, e1_Demo_Results_w]

#
