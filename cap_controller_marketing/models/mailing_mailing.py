# -*- coding: utf-8 -*-
from odoo import fields, models, api, _

class AutomatedRules(models.Model):
    _inherit = "mailing.mailing"

    mailing_list_ids = fields.Many2many('mailing.list', string = "Mailing List")

