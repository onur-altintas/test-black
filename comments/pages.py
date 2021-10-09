from otree.api import Currency as c, currency_range
from ._builtin import Page, WaitPage
from .models import Constants, Player


#### COMMENTS AND DEMOGRAPHICS

class f1_z_Demographics(Page):
    form_model = "player"
    form_fields = ["age", "gender", "education"]

    def vars_for_template(player: Player):
        return{
            'not_baseline': player.participant.vars['treatment'] != 'baseline'
        }
    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds


class f1_z_Comment_t(Page):
    form_model = "player"
    form_fields = ["c_mental", "c_trust", "c_why"]

    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'


class f1_z_Comment_t1(Page):
    form_model = "player"
    form_fields = ["c_gut", "c_AI", "c_data", "c_other"]

    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'

    def error_message(player: Player, values):
        num = 0
        for lang in Constants.comment_t1:
            if values[lang['name']]:
                num += 1
        if num < 1 and values['c_other'] == '':
            return "You must check at least 1 of the first 3 boxes or type for \"Other\" option."


class f1_z_Comments1(Page):
    form_model = "player"
    form_fields = ["c_uperf"]

    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'

    def vars_for_template(self):
        return {
            'c_gut': self.player.c_gut,
            'c_AI': self.player.c_AI,
            'c_data': self.player.c_data,
            'c_other': self.player.c_other
        }

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds


class f1_z_Comments2(Page):
    form_model = "player"
    form_fields = ["c_aiperf"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'


class f1_z_Comments3(Page):
    form_model = "player"
    form_fields = ["c_usage"]

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'


class f1_z_Comments4(Page):
    form_model = "player"
    form_fields = ["c_feel"]

    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'


class f1_z_Comments5(Page):
    form_model = "player"
    form_fields = ["c_usage"]

    def is_displayed(self):
        return self.participant.vars['treatment'] != 'baseline'

    # timer_text = Constants.timer_text
    # get_timeout_seconds = get_timeout_seconds

    def before_next_page(self):
        if self.participant.payoff < 0:
            self.participant.payoff = c(0)

        self.participant.payoff = self.participant.payoff + c(
            self.participant.vars['correct_answers'] / self.session.config['real_world_currency_per_point'] *
            self.session.config['q_pay'])


##### PAYMENT
class f2_Payment(Page):

    def vars_for_template(self):
        if self.participant.payoff < 0:
            self.participant.payoff = c(0)

        cum_profit = self.participant.vars['cum_profit']
        payment = c(max(0, cum_profit)).to_real_world_currency(self.session)
        abs_profit = abs(cum_profit)
        participation_pay = self.session.config['participation_fee']
        full_payment = self.participant.payoff_plus_participation_fee()
        correct_answers = self.participant.vars['correct_answers']
        quiz_pay = round(correct_answers * self.session.config['q_pay'], 2)
        code = self.participant.code
        q_pay = self.session.config['q_pay']
        correct_answers_currency = correct_answers / self.session.config['real_world_currency_per_point'] * q_pay

        return {'cum_profit': cum_profit,
                'payment': payment,
                'abs_profit': abs_profit,
                'participation_pay': participation_pay,
                'full_payment': full_payment,
                'quiz_pay': quiz_pay,
                'participation_quiz': participation_pay + quiz_pay,
                'correct_answers': correct_answers,
                'code': code,
                'rate': int(1 / self.session.config['real_world_currency_per_point']),
                'correct_answers_currency': correct_answers_currency,
                'q_pay': q_pay,
                'payoff': self.participant.payoff,
                'total_pay': full_payment + quiz_pay
                }

    def before_next_page(self):
        self.participant.payoff = self.participant.payoff + c(
            self.participant.vars['correct_answers'] / self.session.config['real_world_currency_per_point'] *
            self.session.config['q_pay'])


page_sequence = [f1_z_Demographics, f1_z_Comment_t, f1_z_Comments3, f1_z_Comment_t1, f1_z_Comments1, f1_z_Comments2,
                 f1_z_Comments4, f2_Payment]
# f1_z_Comments5, ,
