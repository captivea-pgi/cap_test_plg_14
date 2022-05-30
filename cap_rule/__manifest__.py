# -*- coding: utf-8 -*-

{
    'name': 'Règles automatisées',
    'summary': """Creation of automated rules""",
    'description': """
        Creation of automated rules
        """,
    'version': '0.1',
    'author': 'captivea-pgi',
    'website': 'https://www.captivea.com/',
    'category': 'Captivea',
    'depends': [
        'base'
    ],
    'data': [
        'data/ir.model.access.csv',
        'views/automated_rules_views.xml',
        'views/rule_menus.xml',
    ],
}