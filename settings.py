from os import environ

SESSION_CONFIGS = [
    dict(
        name='Interpret_ai',
        display_name="Interpretable AI",
        num_demo_participants=6,
        app_sequence=['Info_module','Demo_module_wo_AI', 'Game_module', 'comments', 'Dropout'],
        hidden_ai=False,
        allocated_time_min=100000,
        demo_rounds=3,
        wo_ai_rounds=5,
        simulation_rounds=30,
        ai_fail_rounds=45,
        use_browser_bots=False,
        ai_column=False,
        q_pay=0.2,
        duration=45,
        demand_type='high'
    ),
    dict(
        name='NV_without_AI',
        display_name="NV without AI",
        num_demo_participants=3,
        app_sequence=['Info_module', 'Demo_module_wo_AI', 'Game_module_wo_AI'],
        hidden_ai=False,
        allocated_time_min=100000,
        demo_rounds=3,
        wo_ai_rounds=30,
        simulation_rounds=30,
        use_browser_bots=False,
        ai_column=False
    )
]
#'Info_module', 'Demo_module_wo_AI', 'Info_module', 'Demo_module_wo_AI',
# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee'] 'Demo_module_wo_AI',

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=0.001, participation_fee=3.00, doc="",
    mturk_hit_settings={
    'keywords': ['easy', 'bonus', 'choice', 'study'],
    'title': 'Buying and Selling Experiment',
    'description': 'Description for your experiment',
    'frame_height': 500,
    'template': 'global/mturk_template.html',
    'minutes_allotted_per_assignment': 45,
    'expiration_hours': 7*24, # 7 days
    #'grant_qualification_id': 'YOUR_QUALIFICATION_ID_HERE',# to prevent retakes
    'qualification_requirements': []
        # qualification.LocaleRequirement("EqualTo", "US"),
        # qualification.PercentAssignmentsApprovedRequirement("GreaterThanOrEqualTo", 50),
        # qualification.NumberHitsApprovedRequirement("GreaterThanOrEqualTo", 5),
        # qualification.Requirement('YOUR_QUALIFICATION_ID_HERE', 'DoesNotExist')
    },
    )

ROOMS = [
    dict(
        name='HM817',
        display_name='HM817',
        participant_label_file='_rooms/test_session.txt',
    ),
    dict(name='Real_session', display_name='Room for live Game_module (no participant labels)'
         ),
]

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True
POINTS_CUSTOM_NAME = 'E$'
POINTS_DECIMAL_PLACES = 0
REAL_WORLD_CURRENCY_DECIMAL_PLACES = 2

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '1a-ghi$yqvu5^ktf)a_wf*otn10jvww8w0+h6iujaj_&fpx3hr'

# if an app is included in SESSION_CONFIGS, you don't need to list it here
#INSTALLED_APPS = ['otree', 'admin_chat']
INSTALLED_APPS = ['otree']
#EXTENSION_APPS = ['admin_chat']

#ROOT_URLCONF = 'admin_chat.urls'
