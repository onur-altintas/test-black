from otree.api import Currency as c, currency_range, widgets
from ._builtin import Page, WaitPage
from .models import Constants

import random

def get_timeout_seconds(player):
    import time
    return player.participant.vars['expiry'] - time.time()


class a_Welcome(Page):
    form_model = "player"
    form_fields = []

    #timer_text = Constants.timer_text
    #get_timeout_seconds = get_timeout_seconds
    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        participation_pay = self.session.config['participation_fee']
        rate = int(1 / self.session.config['real_world_currency_per_point'])

        return {
            'participation_pay': participation_pay,
            'demo_rounds': self.session.config['demo_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'total_rounds': self.session.config['ai_fail_rounds'],
            'rate': rate,
            'duration': self.session.config['duration']
        }

    def before_next_page(self):
        self.participant.vars['hidden_ai'] = self.session.config['hidden_ai']
        self.participant.vars['treatment'] = self.player.treatment


class a_Welcome_class(Page):

    #timer_text = Constants.timer_text
    #get_timeout_seconds = get_timeout_seconds

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        return{
            'demo_rounds': self.session.config['demo_rounds'],
            'simulation_rounds': self.session.config['simulation_rounds'],
            'allocated_time': self.session.config['allocated_time_min'],
            'total_rounds': self.session.config['ai_fail_rounds'],

        }


    def before_next_page(self):
        self.participant.vars['hidden_ai'] = self.session.config['hidden_ai']
        self.participant.vars['treatment'] = self.player.treatment


class b_Consent_info(Page):
    def is_displayed(self):  # this is_display helps to show it only 1 period.
        return self.round_number == 1

    pass


class c_Consent(Page):

    def is_displayed(self):
        return self.round_number == 1

    def vars_for_template(self):
        rate = int(1/self.session.config['real_world_currency_per_point'])
        return{
            'participation_pay': self.session.config['participation_fee'],
            'rate': rate,
            'duration': self.session.config['duration']
        }


class d_Game_info(Page):
    form_model = "player"

    #timer_text = Constants.timer_text
    #get_timeout_seconds = get_timeout_seconds
    def vars_for_template(self):
        return {
            'treatment': self.player.treatment,
            'simulation_rounds': self.session.config['simulation_rounds'],
            'total_rounds': self.session.config['ai_fail_rounds'],

        }

    pass


page_sequence = [a_Welcome, c_Consent, d_Game_info]

#
