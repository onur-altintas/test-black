from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)
from otree.app_template.models import Player

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'comments'
    players_per_group = None
    num_rounds = 1
    gender = ["Female", "Male", "Other", "Prefer Not to Say"]
    education = ["No Degree", "School to a Certain Extent", "High School", "Associate Degree",
                 "Bachelor's degree", "Master's Degree", "Professional Degree", "Doctorate Degree", "Prefer Not to Say"]
    comment1 = [[1, 'Much worse'],
                [2, 'Worse'],
                [3, 'As expected'],
                [4, 'Better'],
                [5, 'Much better']]

    performance = [[1, 'Poor'],
                   [2, 'Fair'],
                   [3, 'Good'],
                   [4, 'Very Good'],
                   [5, 'Excellent']]
    likert5 = [[1, 'Strongly disagree'],
               [2, 'Disagree'],
               [3, 'Neither agree nor disagree'],
               [4, 'Agree'],
               [5, 'Strongly agree']]
    comment_t1 = [dict(name='c_AI', label='BakerAI\'s recommendations'),
                  dict(name='c_gut', label='My intuition'),
                  dict(name='c_data', label='Data')]


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    age = models.PositiveIntegerField(label="What is your age?", min=18, blank=True)
    gender = models.StringField(label=" Which of the following most accurately describes you?",
                                choices=Constants.gender)
    education = models.StringField(label="What is the highest degree or level of school you have completed?",
                                   choices=Constants.education)

    c_uperf = models.IntegerField(
        label="What do you think about your performance?",
        choices=Constants.performance, widget=widgets.RadioSelectHorizontal)
    c_aiperf = models.IntegerField(
        label="What do you think about BakerAI's performance?",
        choices=Constants.performance, widget=widgets.RadioSelectHorizontal)

    c_trust = models.IntegerField(label="I trust BakerAI’s recommendations for optimal long-term profit maximization",
                                  choices=Constants.likert5, widget=widgets.RadioSelectHorizontal)
    c_mental = models.IntegerField(label="I found this task difficult",
                                   choices=Constants.likert5, widget=widgets.RadioSelectHorizontal)
    c_gut = models.BooleanField(initial=False, blank=True)
    c_AI = models.BooleanField(initial=False, blank=True)
    c_data = models.BooleanField(initial=False, blank=True)
    c_other = models.StringField(blank=True)
    c_why = models.LongStringField(label="Please explain why you did or did not trust BakerAI's recommendations")
    c_compare = models.LongStringField(label="Do you think you or BakerAI performed better and why? Please explain "
                                             "it shortly")
    c_feel = models.LongStringField(label="What are your thoughts and feelings about BakerAI?")
    c_usage = models.LongStringField(label="What information would increase your use of BakerAI?")

    pass
