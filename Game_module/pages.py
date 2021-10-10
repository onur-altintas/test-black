from otree.api import *

import random

from Game_module.models import Constants

GROUPS = ['full', 'partial', 'partialc', 'black-box', 'baseline']


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


def ai_rec(demand, pre_ai, round_no, gamma, max_demand, price, cost):
    #    epsilon = (gamma * max_demand) / (max(cost, price - cost) * (round_no + 1) ** (1 / 2))
    epsilon = max_demand / (max(price, cost) * (round_no + 0))
    decrease_h_t = cost
    increase_h_t = -(price - cost)
    if demand <= pre_ai:
        second_term = pre_ai - epsilon * decrease_h_t
    elif demand > pre_ai:
        second_term = pre_ai - epsilon * increase_h_t
    else:
        second_term = -10000

    recommendation = min(max_demand, second_term)
    return round(recommendation)


def get_timeout_seconds(player):
    import time
    return player.participant.vars['expiry'] - time.time()


def is_displayed1(input1, self: Page):
    if input1 == 'dropout':
        dip = self.get_timeout_seconds() < 0
    elif input1 == 'explanation':
        dip = (self.participant.vars['treatment'] == 'partial' or (self.participant.vars['treatment'] == 'full') or \
               (self.participant.vars['treatment'] == 'partialc')) \
              and self.round_number == self.session.config['wo_ai_rounds']
    elif input1 == 'explanation_test':
        dip = (self.participant.vars['treatment'] == 'partial' or (self.participant.vars['treatment'] == 'full')) \
              and self.round_number == self.session.config['wo_ai_rounds']
    elif input1 == 'no_AI':
        dip = self.round_number <= self.session.config['ai_fail_rounds']
    elif input1 == 'ai_recommend':
        dip = self.session.config['wo_ai_rounds'] < self.round_number <= self.session.config['simulation_rounds'] and \
              self.participant.vars['treatment'] != 'baseline'
    elif input1 == 'explanation_intro':
        dip = self.round_number == self.session.config['wo_ai_rounds'] and \
              self.participant.vars['treatment'] != 'baseline'
    elif input1 == 'attention1':
        dip = self.round_number == 1 and self.round_number <= self.session.config['ai_fail_rounds']
    elif input1 == 'attention2':
        dip = self.round_number == 11 and self.round_number <= self.session.config['ai_fail_rounds']
    elif input1 == 'attention3':
        dip = self.round_number == 21 and self.round_number <= self.session.config['ai_fail_rounds']
    else:
        dip = self.round_number <= self.session.config['ai_fail_rounds']
    return dip


class f0_G_no_AI(Page):
    form_model = "player"
    form_fields = ["orderquantity"]

    get_timeout_seconds = get_timeout_seconds

    def is_displayed(self):
        return is_displayed1('no_AI', self)

    def vars_for_template(self):
        self.player.hidden_ai = self.participant.vars['hidden_ai']
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']
        import time
        self.player.participant.vars['expiry'] = time.time() + 600

        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)
        ai_rounds_list = [p.ai_profit_round for p in players]
        ai_profit_list = [p.ai_profit for p in players]
        ai_profitcum_list = [p.ai_profit_cum for p in players]

        self.player.ai_text = "N/A"

        if self.round_number == 1:
            ai_profit_cum = 0
        else:
            ai_profit_cum = players[self.round_number - 2].ai_profit_cum

        return {
            'hist_dem': self.session.vars['historydemand'],
            'round': self.round_number,
            'demand': self.session.vars['demand'][self.round_number - 2],
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'simulation_rounds': self.session.config['simulation_rounds'],
            'simulation_rounds1': self.session.config['simulation_rounds'] + 1,
            'last_round': self.session.config['ai_fail_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'treatment': self.participant.vars['treatment'],
            'rounds_left': self.session.config['ai_fail_rounds'] - self.round_number + 1,
            'ai_left': self.session.config['simulation_rounds'] - self.round_number + 1,
            'is_performance': self.participant.vars['treatment'] == 'performance',
            'ai_profit_cum': ai_profit_cum,
            'ai_rounds_list': ai_rounds_list,
            'ai_profitcum_list': ai_profitcum_list,
            'not_baseline': self.participant.vars['treatment'] != 'baseline',

        }

    def before_next_page(self):
        if self.round_number == self.session.config['wo_ai_rounds']:
            self.player.session.vars['completion_by_treatment'][self.participant.vars['treatment']] += 1
        if self.round_number <= self.session.config['wo_ai_rounds'] or self.round_number > self.session.config[
            'simulation_rounds'] or self.participant.vars['treatment'] == 'baseline':
            self.player.orderquantity2 = self.player.orderquantity
            self.player.demand = self.session.vars['demand'][self.round_number - 1]
            self.player.profit = profit(self.player.demand, self.player.orderquantity2, Constants.sale_price,
                                        Constants.cost)
            self.player.sales = min(self.player.demand, self.player.orderquantity2)
            self.player.revenue = self.player.sales * Constants.sale_price
            self.player.cost = self.player.orderquantity2 * Constants.cost
            self.player.leftover = self.player.orderquantity2 - self.player.sales
            self.player.payoff = self.player.profit
            self.player.ai_recommend = self.player.sales
            self.player.demand_quantity_dif = - self.player.demand + self.player.orderquantity2

        if self.round_number > self.session.config['simulation_rounds']:
            self.player.ai_profit_cum = self.player.in_round(self.player.round_number - 1).ai_profit_cum + \
                                        profit(self.player.demand, self.player.orderquantity2, Constants.sale_price,
                                               Constants.cost)

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f0_G_AA(Page):
    form_model = "player"
    form_fields = ["orderquantity2"]

    # timer_text = Constants.timer_text
    get_timeout_seconds = get_timeout_seconds

    def is_displayed(self):
        return is_displayed1('ai_recommend', self)

    def vars_for_template(self):
        self.player.hidden_ai = self.participant.vars['hidden_ai']
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']

        players = self.player.in_previous_rounds()
        oq_now = self.player.in_round(self.round_number).orderquantity
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        if self.round_number == self.session.config['wo_ai_rounds'] + 1:
            ai_recommendation = 300
        else:
            p_demand = players[self.round_number - 2].demand
            p_ai = players[self.round_number - 2].ai_recommend
            p_round = self.round_number - 1

            ai_recommendation = ai_rec(p_demand, p_ai, p_round, Constants.gamma, Constants.max_demand,
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
            'last_round': self.session.config['ai_fail_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'ai_recommendation': ai_recommendation,
            'treatment': self.participant.vars['treatment'],
            'ai_text': self.player.ai_text,
            'rounds_left': self.session.config['ai_fail_rounds'] - self.round_number + 1,
            'ai_left': self.session.config['simulation_rounds'] - self.round_number + 1,
            'oq_now': oq_now,
            'is_performance': self.participant.vars['treatment'] == 'performance',
            'ai_profit_cum': players[self.round_number - 2].ai_profit_cum,
            'not_baseline': self.participant.vars['treatment'] != 'baseline'
        }

    def before_next_page(self):
        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.profit = profit(self.player.demand, self.player.orderquantity2, Constants.sale_price,
                                    Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity2)
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity2 * Constants.cost
        self.player.leftover = self.player.orderquantity2 - self.player.sales
        self.player.payoff = self.player.profit
        self.player.demand_quantity_dif = -self.player.demand + self.player.orderquantity2

        if self.round_number == self.session.config['wo_ai_rounds'] + 1:
            self.participant.vars['pre_profit'] = sum([p.profit for p in self.player.in_previous_rounds()])
            # self.player.ai_profit = self.participant.vars['pre_profit'] + \
            #                        profit(self.player.demand,
            #                               self.session.vars['ai_counterfact_rec'][self.round_number - 6],
            #                               Constants.sale_price, Constants.cost)
            self.player.ai_profit_round = profit(self.player.demand, self.player.ai_recommend, Constants.sale_price,
                                                 Constants.cost)
            self.player.ai_profit_cum = self.participant.vars['pre_profit'] + \
                                        self.player.ai_profit_round
        elif self.round_number <= self.session.config['simulation_rounds']:
            # self.player.ai_profit = self.player.in_round(self.player.round_number - 1).ai_profit + \
            #                        profit(self.player.demand,
            #                               self.session.vars['ai_counterfact_rec'][self.round_number - 6],
            #                               Constants.sale_price, Constants.cost)
            self.player.ai_profit_round = profit(self.player.demand, self.player.ai_recommend, Constants.sale_price,
                                                 Constants.cost)
            self.player.ai_profit_cum = self.player.in_round(self.player.round_number - 1).ai_profit_cum + \
                                        self.player.ai_profit_round

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f0_Results(Page):
    form_model = "player"
    form_fields = ["ai_trust"]
    # timer_text = Constants.timer_text
    get_timeout_seconds = get_timeout_seconds

    #
    def is_displayed(self):
        return is_displayed1('', self)

    def vars_for_template(self):
        demand = self.session.vars['demand'][self.round_number - 1]
        players = self.player.in_all_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)
        self.participant.vars['cum_profit'] = cum_profit
        extra_time = (self.round_number % 5 == 0 and self.round_number > self.session.config['wo_ai_rounds']) * \
                     min(Constants.wait_every5 * (self.round_number / 5) + 10, 20) * \
                     (self.round_number != self.session.config['ai_fail_rounds'])


        return {
            'round': self.round_number,
            'demand': demand,
            'player_in_all_rounds': players,
            'cum_profit': cum_profit,
            'abs_profit': abs(self.player.profit),
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'last_round': self.session.config['ai_fail_rounds'],
            'extra_time': extra_time,
            'is_round_5': ((self.round_number % 5 == 0) and (self.round_number > self.session.config['wo_ai_rounds'])
                           and (self.round_number <= self.session.config['simulation_rounds'])),
            'test': self.participant.vars['pre_profit'],
            'ai_profit': self.player.ai_profit,
            'is_performance': self.participant.vars['treatment'] == 'performance',
            'not_baseline': self.participant.vars['treatment'] != 'baseline',
            'ai_profit_cum': self.player.ai_profit_cum,
            'is_ai_rounds': (self.session.config['simulation_rounds'] >= self.round_number > self.session.config[
                'wo_ai_rounds']),
            'is_round_10': (self.round_number % 10 == 0) and self.round_number <= self.session.config['simulation_rounds']
        }

    def before_next_page(self):
        self.player.treatment = self.participant.vars['treatment']
        if self.round_number == self.session.config['ai_fail_rounds']:
            players = self.player.in_all_rounds()
            profits = [p.profit for p in players]
            cum_profit = sum(profits)
            self.participant.vars['cum_profit'] = cum_profit
            self.player.cum_profit = cum_profit

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class e1_T_intro(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return is_displayed1('explanation_intro', self)

    def vars_for_template(self):
        return {
            'treatments': self.participant.vars['treatment'],
            'round_plus': self.round_number + 1,
            'trial_period': self.session.config['simulation_rounds'] - self.session.config['wo_ai_rounds']
        }

    def before_next_page(self):
        import time
        self.player.participant.vars['expiry'] = time.time() + 900


class e2_T(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds

    def vars_for_template(self):
        return {
            'treatment': self.participant.vars['treatment']
        }

    def is_displayed(self):
        return is_displayed1('explanation', self)


class e3_T_test(Page):
    form_model = "player"
    form_fields = ["treatment_test1", "treatment_test2"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return is_displayed1('explanation_test', self)

    def vars_for_template(self):
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        return {
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
        }


class f1_A(Page):
    form_model = 'player'
    form_fields = ['attention_model_cost', 'attention_demand']

    def is_displayed(self):
        return is_displayed1('attention1', self)

    def vars_for_template(self):
        return {
            'q_pay': self.session.config['q_pay']
        }

    def before_next_page(self):
        self.participant.vars['treatment'] = min(GROUPS, key=lambda color:
        self.subsession.session.vars['completion_by_treatment'][color])
        self.player.treatment = self.participant.vars['treatment']

        self.participant.vars['correct_answers'] = 0
        if self.player.attention_model_cost == Constants.cost:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_demand == 600:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f1_A_f(Page):
    def is_displayed(self):
        return is_displayed1('attention1', self)

    def vars_for_template(self):
        return {
            'q_pay': self.session.config['q_pay'],
            'cost_answer': self.player.attention_model_cost,
            'demand_answer': self.player.attention_demand,
            'demand_true': self.player.attention_demand == 600,
            'cost_true': self.player.attention_model_cost == Constants.cost,
        }

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened and self.session.config['wo_ai_rounds'] < self.round_number:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f1_A2(Page):
    form_model = 'player'
    form_fields = ['attention_model_sale', 'attention_profit']

    def is_displayed(self):
        return is_displayed1('attention2', self)

    def vars_for_template(self):
        return {
            'q_pay': self.session.config['q_pay'],
            'selection': max(int(self.participant.vars['cum_profit'] / 2000), -1),
            'cum_profit': self.participant.vars['cum_profit'],
            'test': int(int(self.participant.vars['cum_profit']) / 2000),
            'not_baseline': self.participant.vars['treatment'] != 'baseline',
        }

    def before_next_page(self):

        if self.player.attention_model_sale == Constants.sale_price:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_profit == max(int(int(self.participant.vars['cum_profit']) / 2000), -1):
            self.player.profit_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened and self.session.config['wo_ai_rounds'] < self.round_number:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f1_A2_f(Page):
    def is_displayed(self):
        return is_displayed1('attention2', self)

    def vars_for_template(self):
        return {
            'q_pay': self.session.config['q_pay'],
            'sale_answer': self.player.attention_model_sale,
            'cumprofit_correct_answer': str(
                "'" + Constants.profit_choice[max(int(int(self.participant.vars['cum_profit']) / 2000), -1) + 1][
                    1] + "'"),
            'profit_true': self.player.profit_true,
            'sale_true': self.player.attention_model_sale == Constants.sale_price,
            'correct_sale': Constants.sale_price,
            'cumprofit_answer': str("'" + Constants.profit_choice[self.player.attention_profit + 1][1] + "'"),
            'attention_profit': self.player.attention_profit,
            'current_cumprofit': self.participant.vars['cum_profit']
        }

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened and self.session.config['wo_ai_rounds'] < self.round_number:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f1_A3(Page):
    form_model = 'player'
    form_fields = ['attention_loss', 'attention_profit']

    def is_displayed(self):
        return is_displayed1('attention3', self)

    def vars_for_template(self):

        return {
            'equal': max(self.participant.vars['cum_profit'] / 2000, -1),
            'q_pay': self.session.config['q_pay'],
            'not_baseline': self.participant.vars['treatment'] != 'baseline',
        }

    def before_next_page(self):

        if self.player.attention_loss == Constants.cost:
            self.player.answer_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

        if self.player.attention_profit == max(int(int(self.participant.vars['cum_profit']) / 2000), -1):
            self.player.profit_true = True
            self.player.correct_answers = self.player.correct_answers + 1
            self.participant.vars['correct_answers'] = self.participant.vars['correct_answers'] + 1

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened and self.session.config['wo_ai_rounds'] < self.round_number:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


class f1_A3_f(Page):
    def is_displayed(self):
        return is_displayed1('attention3', self)

    def vars_for_template(self):
        return {
            'q_pay': self.session.config['q_pay'],
            'loss_answer': self.player.attention_loss,
            'cumprofit_correct_answer': str(
                "'" + Constants.profit_choice[max(int(int(self.participant.vars['cum_profit']) / 2000), -1) + 1][
                    1] + "'"),
            'profit_true': self.player.profit_true,
            'loss_true': self.player.attention_loss == Constants.cost,
            'correct_loss': Constants.cost,
            'cumprofit_answer': str("'" + Constants.profit_choice[self.player.attention_profit + 1][1] + "'"),
            'current_cumprofit': self.participant.vars['cum_profit']

        }

    def app_after_this_page(self, upcoming_apps):
        if self.timeout_happened and self.session.config['wo_ai_rounds'] < self.round_number:
            self.session.vars['completion_by_treatment'][self.player.participant.vars['treatment']] -= 1
            return upcoming_apps[-1]


page_sequence = [f1_A, f1_A_f, f1_A2, f1_A2_f, f1_A3, f1_A3_f,
                 f0_G_no_AI, f0_G_AA, f0_Results, e1_T_intro,
                 e2_T, e3_T_test]

# page_sequence = [f0_Game_wo_AI, f1_Results_wo_AI, e1_Treatment_intro, e2_Treatment, e3_Treatment_test, f0_Game,
# f1_Results, f1_z_Comments1, f1_z_Comments2, f1_z_Comments3,
# f1_z_Demographics,
# f2_Payment_class]
