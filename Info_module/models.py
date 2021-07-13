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
Information 
"""

class Constants(BaseConstants):
    name_in_url = 'Info_module'
    players_per_group = None
    #timer_text = 'Time to complete the simulation (min:sec):'
    num_rounds = 1
    gender = ["Female", "Male", "Other", "Prefer Not to Say"]
    instructions_template = 'Info_module/z_instructions_intro.html'
    irb_consent = 'Info_module/z_consent_irb_version.html'
    info_sheet = 'Info_module/z_consent.html'
    welcome_template = 'Info_module/z_welcome_template.html'
    #welcome_template_class = 'Info_module/z_welcome_template_class.html'
    cost = 3
    sale_price = 4
    base_pay = 3
    wait_game = 20


class Subsession(BaseSubsession):

    def creating_session(self):
        # Assigning Treatment variables
        import itertools
        # turn_treatment = itertools.cycle(['baseline', 'black-box', 'partial', 'full', 'performance'])
        turn_treatment = itertools.cycle(['baseline', 'black-box', 'performance'])

        for player in self.get_players():
            player.treatment = next(turn_treatment)

        import time
        for p in self.get_players():
            p.participant.vars['expiry'] = time.time() + self.session.config['allocated_time_min']*60


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    hidden_ai = models.BooleanField(label="Would you like the AI recommended quantities to be hidden? (version choice)",
                                    choices=[[True, 'Yes (hidden)'], [False, 'No (visible)']], widget=widgets.RadioSelect)

    treatment = models.StringField()
