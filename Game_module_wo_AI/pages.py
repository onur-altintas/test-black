from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants

import random


def profit(demand, orderquantity, sale, cost):
    prof = min(demand, orderquantity) * sale - orderquantity * cost
    return prof


def get_timeout_seconds(player):
    import time
    return player.participant.vars['expiry'] - time.time()


class f0_Game_no_AI(Page):
    form_model = "player"
    form_fields = ["orderquantity"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds

    def is_displayed(self):
        return self.round_number <= self.session.config['wo_ai_rounds']

    def vars_for_template(self):
        wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
        # self.player.treatment = self.participant.vars['treatment']

        players = self.player.in_previous_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        return {
            'hist_dem': self.session.vars['historydemand'],
            'round': self.round_number,
            'demand': self.session.vars['demand'][self.round_number - 2],
            'player_in_prev_rounds': players,
            'profit': profits,
            'cum_profit': cum_profit,
            'simulation_rounds': self.session.config['wo_ai_rounds'],
            'wo_ai_rounds1': wo_ai_rounds1,
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'rounds_left': self.session.config['wo_ai_rounds'] - self.round_number + 1

        }

    def before_next_page(self):
        self.player.demand = self.session.vars['demand'][self.round_number - 1]
        self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
        self.player.sales = min(self.player.demand, self.player.orderquantity)
        self.player.revenue = self.player.sales * Constants.sale_price
        self.player.cost = self.player.orderquantity * Constants.cost
        self.player.leftover = self.player.orderquantity - self.player.sales
        self.player.payoff = self.player.profit


class f1_Results_wo_AI(Page):
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    #
    def is_displayed(self):
        return self.round_number <= self.session.config['wo_ai_rounds']

    def vars_for_template(self):
        demand = self.session.vars['demand'][self.round_number - 1]
        players = self.player.in_all_rounds()
        profits = [p.profit for p in players]
        cum_profit = sum(profits)

        return {
            'round': self.round_number,
            'demand': demand,
            'player_in_all_rounds': players,
            'cum_profit': cum_profit,
            'abs_profit': abs(self.player.profit),
            'wo_ai_rounds': self.session.config['wo_ai_rounds'],
            'simulation_rounds': self.session.config['wo_ai_rounds'],
            'extra_time': (self.round_number % 5 == 0) * Constants.wait_every5
        }

    def before_next_page(self):
        if self.round_number == self.session.config['wo_ai_rounds']:
            players = self.player.in_all_rounds()
            profits = [p.profit for p in players]
            cum_profit = sum(profits)
            self.participant.vars['cum_profit'] = cum_profit


class f1_z_Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education", 'comment']

    def is_displayed(self):
        return self.round_number == self.session.config['wo_ai_rounds']


class f2_Payment(Page):

    def is_displayed(self):
        return self.round_number == self.session.config['wo_ai_rounds']

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


class f1_z_Attention(Page):
    form_model = 'player'
    form_fields = ['attention_model_cost', 'attention_demand']

    def is_displayed(self):
        return self.round_number == 1

    def before_next_page(self):
        if self.player.attention_model_cost == 3 and self.player.attention_demand == 300:
            self.player.answer_true = True


class f1_z_Attention2(Page):
    form_model = 'player'
    form_fields = ['attention_model_sale', 'attention_profit']

    def is_displayed(self):
        return self.round_number == 11

    def before_next_page(self):
        if self.player.attention_model_sale == 4:
            self.player.answer_true = True

        if self.player.attention_profit == max(int(sum([p.profit for p in self.player.in_previous_rounds()])/200), -1):
            self.player.profit_true = True


class f1_z_Attention3(Page):
    form_model = 'player'
    form_fields = ['attention_loss', 'attention_profit']

    def vars_for_template(self):

        return{
        'equal': max(int(sum([p.profit for p in self.player.in_previous_rounds()])/200), -1)
        }

    def is_displayed(self):
        return self.round_number == 21

    def before_next_page(self):
        if self.player.attention_loss == 3:
            self.player.answer_true = True

        if self.player.attention_profit == max(int(sum([p.profit for p in self.player.in_previous_rounds()])/200), -1):
            self.player.profit_true = True


page_sequence = [f1_z_Attention, f1_z_Attention2, f1_z_Attention3,
                 f0_Game_no_AI, f1_Results_wo_AI, f1_z_Demographics, f2_Payment]

# page_sequence = [f0_Game_wo_AI, f1_Results_wo_AI, e1_Treatment_intro, e2_Treatment, e3_Treatment_test, f0_Game,
# f1_Results, f1_z_Comments1, f1_z_Comments2, f1_z_Comments3,
# f1_z_Demographics,
# f2_Payment_class]

{
    # a_Welcome, b_Consent_info, c_Consent,

    # class f0_Game(Page):
    #     form_model = "player"
    #     form_fields = ["orderquantity", "ai_click", "submit_ai"]
    #
    #     # timer_text = Constants.timer_text
    #     # get_timeout_seconds = get_timeout_seconds
    #     def is_displayed(self):
    #         return self.session.config['wo_ai_rounds'] < self.round_number <= self.session.config['simulation_rounds']
    #
    #     def vars_for_template(self):
    #         self.player.hidden_ai = self.participant.vars['hidden_ai']
    #         hist_dem = self.session.vars['historydemand']
    #         demand = self.session.vars['demand'][self.round_number - 2]
    #         players = self.player.in_previous_rounds()
    #         profits = [p.profit for p in players]
    #         cum_profit = sum(profits)
    #         wo_ai_rounds1 = self.session.config['wo_ai_rounds'] + 1
    #
    #         # AI Recommendation
    #         if self.round_number == 1:
    #             ai_recommendation = -1
    #         else:
    #             p_sales = players[self.round_number - 2].sales
    #             p_order = players[self.round_number - 2].orderquantity
    #             p_ai = players[self.round_number - 2].ai_recommend
    #             p_round = self.round_number - 1
    #
    #             ai_recommendation = ai_rec(p_sales, p_order, p_ai, p_round, Constants.gamma, Constants.max_demand,
    #                                        Constants.sale_price, Constants.cost)
    #
    #         self.player.ai_recommend = ai_recommendation
    #
    #         if self.player.hidden_ai:
    #             ai_text = "Quantity will be determined by the A.I."
    #         else:
    #             ai_text = str(ai_recommendation) + " loaves"
    #         return {
    #             'hist_dem': hist_dem,
    #             'round': self.round_number,
    #             'demand': demand,
    #             'player_in_prev_rounds': players,
    #             'profit': profits,
    #             'cum_profit': cum_profit,
    #             'ai_recommendation': ai_recommendation,
    #             'ai_text': ai_text,
    #             'wo_ai_rounds1': wo_ai_rounds1,
    #             'wo_ai_rounds': self.session.config['wo_ai_rounds'],
    #             'simulation_rounds': self.session.config['simulation_rounds'],
    #             'ai_column': self.session.config['ai_column'],
    #
    #         }
    #
    #     def before_next_page(self):
    #         self.player.demand = self.session.vars['demand'][self.round_number - 1]
    #         self.player.profit = profit(self.player.demand, self.player.orderquantity, Constants.sale_price, Constants.cost)
    #         self.player.sales = min(self.player.demand, self.player.orderquantity)
    #         self.player.revenue = self.player.sales * Constants.sale_price
    #         self.player.cost = self.player.orderquantity * Constants.cost
    #         self.player.leftover = self.player.orderquantity - self.player.sales
    #         self.player.payoff = self.player.profit

    # class f1_Results(Page):
    #
    #     def is_displayed(self):
    #         return self.session.config['wo_ai_rounds'] < self.round_number <= self.session.config['simulation_rounds']
    #
    #     # timer_text = Constants.timer_text
    #     # get_timeout_seconds = get_timeout_seconds
    #     def vars_for_template(self):
    #         demand = self.session.vars['demand'][self.round_number - 1]
    #         players = self.player.in_all_rounds()
    #         profits = [p.profit for p in players]
    #         cum_profit = sum(profits)
    #
    #         return {
    #             'round': self.round_number,
    #             'demand': demand,
    #             'player_in_all_rounds': players,
    #             'cum_profit': cum_profit,
    #             'abs_profit': abs(self.player.profit),
    #             'test': sum([p.payoff for p in players]),
    #             'wo_ai_rounds': self.session.config['wo_ai_rounds'],
    #             'simulation_rounds': self.session.config['simulation_rounds'],
    #             'ai_column': self.session.config['ai_column'],
    #
    #         }
}
