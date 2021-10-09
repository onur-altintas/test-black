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

class Subsession(BaseSubsession):
    pass


class Constants(BaseConstants):
    name_in_url = 'Info_module'
    players_per_group = None
    #timer_text = 'Time to complete the simulation (min:sec):'
    num_rounds = 1
    instructions_template = 'Info_module/z_instructions_intro.html'
    irb_consent = 'Info_module/z_consent_irb_version.html'
    info_sheet = 'Info_module/z_consent.html'
    welcome_template = 'Info_module/z_welcome_template.html'
    #welcome_template_class = 'Info_module/z_welcome_template_class.html'
    cost = 2
    sale_price = 4
    base_pay = 3
    wait_game = 20





class Group(BaseGroup):
    pass


class Player(BasePlayer):
    hidden_ai = models.BooleanField(label="Would you like the AI recommended quantities to be hidden? (version choice)",
                                    choices=[[True, 'Yes (hidden)'], [False, 'No (visible)']], widget=widgets.RadioSelect)

