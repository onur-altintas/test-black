from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import random


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


def ai_rec(sales, orderquantity, pre_ai, round_no, gamma, max_demand, price, cost):
    #    epsilon = (gamma * max_demand) / (max(cost, price - cost) * (round_no + 1) ** (1 / 2))
    epsilon = max_demand / (max(price, cost) * (round_no + 5))
    if sales == orderquantity and sales < pre_ai:
        # print("ai high,order=sales")
        increase_h_t = -(price - cost)
        decrease_h_t = cost
        rec1 = orderquantity - epsilon * increase_h_t
        rec2 = pre_ai - epsilon * decrease_h_t
        # second_term = rec1 + max(rec2 / 2 - rec1 / 2, 0)
        second_term = rec1
    elif pre_ai > sales and orderquantity > sales:
        # print("both high")
        decrease_h_t = cost
        second_term = min(orderquantity, pre_ai) - epsilon * decrease_h_t
    elif sales == orderquantity and sales >= pre_ai:
        # print("sales=order>=ai")
        increase_h_t = -(price - cost)
        second_term = orderquantity - epsilon * increase_h_t
    elif orderquantity > sales and sales == pre_ai:
        # print("sales=order>=ai")
        decrease_h_t = cost
        second_term = sales - epsilon * decrease_h_t
    elif orderquantity > sales > pre_ai:
        # print("order high,ai low")
        increase_h_t = -(price - cost)
        decrease_h_t = cost
        # rec1 = orderquantity - epsilon * decrease_h_t
        rec2 = pre_ai - epsilon * increase_h_t
        second_term = rec2
        # + max(min(rec1, max_demand) / 2 - rec2 / 2, 0)
    else:
        second_term = -10000

    recommendation = min(max_demand, second_term)
    return round(recommendation)


def get_timeout_seconds(player):
    import time
    return player.participant.vars['expiry'] - time.time()


class f0_G_no_AI(Page):
    form_model = "player"
    form_fields = ["orderquantity"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.round_number <= self.session.config['wo_ai_rounds']

    def vars_for_template(self):
        self.player.hidden_ai = self.participant.vars['hidden_ai']
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']

        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        self.player.ai_text = "N/A"

        return {
            'hist_dem': self.session.vars['historydemand'],
            'round': self.round_number,
            'demand': self.session.vars['demand'][self.round_number - 2],
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'simulation_rounds': self.session.config['simulation_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'treatment': self.participant.vars['treatment'],
            'rounds_left': self.session.config['simulation_rounds'] - self.round_number + 1

        }

    def before_next_page(self):
        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity)
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity * Constants.cost
        self.player.leftover = self.player.orderquantity - self.player.sales
        self.player.payoff = self.player.profit
        self.player.ai_recommend = self.player.sales


class f0_G_WOA(Page):
    live_method = "live_oq"
    form_model = "player"
    form_fields = ["orderquantity", "keep_q"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.session.config['wo_ai_rounds'] < self.round_number <= self.session.config['simulation_rounds']

    def vars_for_template(self):
        self.player.hidden_ai = self.participant.vars['hidden_ai']
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']

        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        oq = self.player.order_wip

        if self.round_number == self.session.config['wo_ai_rounds'] + 1:
            ai_recommendation = 70
        else:
            p_sales = players[self.round_number - 2].sales
            p_order = players[self.round_number - 2].orderquantity
            p_ai = players[self.round_number - 2].ai_recommend
            p_round = self.round_number - 1

            ai_recommendation = ai_rec(p_sales, p_order, p_ai, p_round, Constants.gamma, Constants.max_demand,
                                       Constants.sale_price, Constants.cost)

        self.player.ai_recommend = ai_recommendation

        self.player.ai_text = str(ai_recommendation) + " loaves"

        return {
            'hist_dem': self.session.vars['historydemand'],
            'round': self.round_number,
            'demand': self.session.vars['demand'][self.round_number - 2],
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'simulation_rounds': self.session.config['simulation_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'ai_recommendation': ai_recommendation,
            'oq': oq,
            'treatment': self.participant.vars['treatment'],
            'ai_text': self.player.ai_text,
            'rounds_left': self.session.config['simulation_rounds'] - self.round_number + 1
        }

    def before_next_page(self):
        if self.player.orderquantity2 == 0:
            self.player.orderquantity = self.player.order_wip
        else:
            self.player.orderquantity = self.player.orderquantity2

        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity)
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity * Constants.cost
        self.player.leftover = self.player.orderquantity - self.player.sales
        self.player.payoff = self.player.profit


class f0_G_WOA1(Page):
    live_method = "live_oq"
    form_model = "player"
    form_fields = ["orderquantity", "keep_q"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.session.config['wo_ai_rounds'] < self.round_number <= self.session.config['simulation_rounds']

    def vars_for_template(self):
        self.player.hidden_ai = self.participant.vars['hidden_ai']
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']

        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        oq = self.player.order_wip

        if self.round_number == self.session.config['wo_ai_rounds'] + 1:
            ai_recommendation = 70
        else:
            p_sales = players[self.round_number - 2].sales
            p_order = players[self.round_number - 2].orderquantity
            p_ai = players[self.round_number - 2].ai_recommend
            p_round = self.round_number - 1

            ai_recommendation = ai_rec(p_sales, p_order, p_ai, p_round, Constants.gamma, Constants.max_demand,
                                       Constants.sale_price, Constants.cost)

        self.player.ai_recommend = ai_recommendation

        self.player.ai_text = str(ai_recommendation) + " loaves"

        return {
            'hist_dem': self.session.vars['historydemand'],
            'round': self.round_number,
            'demand': self.session.vars['demand'][self.round_number - 2],
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'simulation_rounds': self.session.config['simulation_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'ai_recommendation': ai_recommendation,
            'oq': oq,
            'treatment': self.participant.vars['treatment'],
            'ai_text': self.player.ai_text,
            'rounds_left': self.session.config['simulation_rounds'] - self.round_number + 1
        }

    def before_next_page(self):
        if self.player.orderquantity2 == 0:
            self.player.orderquantity = self.player.order_wip
        else:
            self.player.orderquantity = self.player.orderquantity2

        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity)
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity * Constants.cost
        self.player.leftover = self.player.orderquantity - self.player.sales
        self.player.payoff = self.player.profit


class f1_Results(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    #
    def is_displayed(self):
        return self.round_number <= self.session.config['simulation_rounds']

    def vars_for_template(self):
        demand = self.session.vars['demand'][self.round_number - 1]
        players = self.player.in_all_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)
        self.participant.vars['cum_profit'] = cum_profit
        return {
            'round': self.round_number,
            'demand': demand,
            'player_in_all_rounds': players,
            'cum_profit': cum_profit,
            'abs_profit': abs(self.player.profit),
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'extra_time': (self.round_number % 5 == 0) * Constants.wait_every5 * (self.round_number / 5) * (self.round_number!=self.session.config['simulation_rounds'])
        }

    def before_next_page(self):
        if self.round_number == self.session.config['simulation_rounds']:
            players = self.player.in_all_rounds()
            profits = [p.profit for p in players]
            cum_profit = sum(profits)
            self.participant.vars['cum_profit'] = cum_profit


class e1_T_intro(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.round_number == self.session.config['wo_ai_rounds']

    def vars_for_template(self):
        return {
            'treatments': self.participant.vars['treatment'],
            'round_plus': self.round_number + 1,
        }


class e2_T(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds

    def vars_for_template(self):
        return {
            'treatment': self.participant.vars['treatment']
        }

    def is_displayed(self):
        return (self.participant.vars['treatment'] != 'control') and self.round_number == self.session.config[
            'wo_ai_rounds']


class e3_T_test(Page):
    form_model = "player"
    form_fields = ["treatment_test1", "treatment_test2"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return (self.participant.vars['treatment'] != 'control') and self.round_number == self.session.config[
            'wo_ai_rounds']

    def vars_for_template(self):
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        return {
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
        }


class f2_Payment_class(Page):
    def is_displayed(self):
        return self.round_number == self.session.config['simulation_rounds']

    def vars_for_template(self):
        if self.participant.payoff < 0:
            self.participant.payoff = c(0)

        players = self.player.in_all_rounds()
        cum_profit = sum([p.profit for p in players])
        payment = c(max(0, cum_profit)).to_real_world_currency(self.session)
        abs_profit = abs(cum_profit)
        participation_pay = self.session.config['participation_fee']
        full_payment = self.participant.payoff_plus_participation_fee()
        code = self.participant.code

        return {'cum_profit': cum_profit,
                'payment': payment,
                'abs_profit': abs_profit,
                'participation_pay': participation_pay,
                'full_payment': full_payment,
                'code': code}


class f1_z_A(Page):
    form_model = 'player'
    form_fields = ['attention_model_cost', 'attention_demand']

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return{
            'q_pay': self.session.config['q_pay']
        }

    def before_next_page(self):
        self.participant.vars['correct_answers'] = 0
        if self.player.attention_model_cost == 3:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_demand == 300:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1


class f1_z_A2(Page):
    form_model = 'player'
    form_fields = ['attention_model_sale', 'attention_profit']

    def is_displayed(self):
        return self.round_number == 11 and self.round_number <= self.session.config['simulation_rounds']

    def vars_for_template(self):
        return{
            'q_pay': self.session.config['q_pay'],
            'selection': max(int(self.participant.vars['cum_profit']/200), -1),
            'cum_profit': self.participant.vars['cum_profit'],
            'test': int(int(self.participant.vars['cum_profit'])/200)
        }

    def before_next_page(self):
        if self.player.attention_model_sale == 4:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_profit == max(int(int(self.participant.vars['cum_profit'])/200), -1):
            self.player.profit_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1


class f1_z_A3(Page):
    form_model = 'player'
    form_fields = ['attention_loss', 'attention_profit']

    def is_displayed(self):
        return self.round_number == 21 and self.round_number <= self.session.config['simulation_rounds']

    def vars_for_template(self):

        return {
            'equal': max(self.participant.vars['cum_profit']/200, -1),
            'q_pay': self.session.config['q_pay']
        }

    def before_next_page(self):
        if self.player.attention_loss == 3:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_profit == max(int(int(self.participant.vars['cum_profit'])/200), -1):
            self.player.profit_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1


page_sequence = [f1_z_A, f1_z_A2, f1_z_A3,
                 f0_G_no_AI, f0_G_WOA, f1_Results, e1_T_intro,
                 e2_T, e3_T_test]

# page_sequence = [f0_Game_wo_AI, f1_Results_wo_AI, e1_Treatment_intro, e2_Treatment, e3_Treatment_test, f0_Game,
# f1_Results, f1_z_Comments1, f1_z_Comments2, f1_z_Comments3,
# f1_z_Demographics,
# f2_Payment_class]

