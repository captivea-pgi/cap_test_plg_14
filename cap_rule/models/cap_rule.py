# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from datetime import *
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class AutomatedRules(models.Model):
    _name = "automated.rules"
    _description = "Automated Rules Management"

    name = fields.Char(required=True)
    action_id = fields.Many2one('base.automation', string = "Linked action")
    selector1 = fields.Selection(
        string='Et / Ou',
        selection=[
            ('et', 'ET'),
            ('ou', 'OU'),
        ],
        default = 'et',
    )
    selector2 = fields.Selection(
        string='Et / Ou',
        selection=[
            ('et', 'ET'),
            ('ou', 'OU'),
        ],
        default='et',
    )
    operator_sender = fields.Selection(
        selection=[
            ('==', '=='),
            ('in', 'in'),
        ],
        default='in',
        nolabel=1,
    )
    operator_object = fields.Selection(
        selection=[
            ('==', '=='),
            ('in', 'in'),
        ],
        default='in',
        nolabel=1,
    )
    operator_body = fields.Selection(
        selection=[
            ('==', '=='),
            ('in', 'in'),
        ],
        default='in',
        nolabel=1,
    )
    sender = fields.Char(string="Expéditeur")
    object = fields.Char(string="Sujet du mail")
    body = fields.Char(string="Corps du message")

    stage_id = fields.Many2one("helpdesk.stage", string="Status du ticket")
    team_id = fields.Many2one("helpdesk.team", string="Equipe assistance")
    model_id = fields.Many2one("mail.template", string="Modèle d'email")
    priority = fields.Selection(
        string='Priorité ticket',
        selection=[
            ('0', 'Normal'),
            ('1', 'Low'),
            ('2', 'High'),
            ('3', 'Very High'),
        ]
    )
    user_id = fields.Many2one("res.users", string="Assigné à")

    description = fields.Text(string="Description")
    generatedCode = fields.Text(string="Code Python")

    def _generate_condition(self, sender, object, body):
        selector1 = "or" if self.selector1 == 'ou' else "and"
        selector2 = "or" if self.selector2 == 'ou' else "and"
        rule_dict = {}
        rule_keys = ['email_from', 'subject', 'body']
        rule_values = [sender, object, body]
        rule_operator = [self.operator_sender, self.operator_object, self.operator_body]

        for i in range(len(rule_keys)):
            if rule_values[i]:
                rule_dict[rule_keys[i]] = "\"" + rule_values[i] + "\""

        if len(rule_dict) < 3:
            return f" {selector1} ".join(f"record.{k} {rule_operator[list(rule_dict.keys()).index(k)]} {v}" for k, v in rule_dict.items())
        else:
            s = (f" {selector1} ".join(f'record.{k} {rule_operator[list(rule_dict.keys()).index(k)]} {v}' for k, v in rule_dict.items()))
            index = s.rfind(' ' + selector1 + ' ')
            return s[:index] + ' ' + selector2 + ' ' + s[index + len(' ' + selector1 + ' '):]

    def _generate_action(self, actions, priority):
        action_dict = {}
        action_keys = ['stage_id', 'team_id', 'model_id', 'user_id']

        for i in range(len(action_keys)):
            if actions[i]:
                action_dict[action_keys[i]] = actions[i]

        result = f"        ".join(f"record['{k}'] = {v.id} \n" for k, v in action_dict.items())
        result += f"            record['priority'] = {priority}" if priority else ''

        return result

    @api.onchange('selector1', 'selector2', 'sender', 'object', 'body', 'stage_id', 'team_id', 'model_id', 'user_id', 'priority', 'operator_sender', 'operator_object', 'operator_body')
    def _generate_python_code(self):
        indent = "            " if self.stage_id or self.team_id or self.model_id or self.user_id else ""
        condition = f"for record in records: \n" \
                    f"    if record.message_type == 'email': \n" \
                    f"        if {self._generate_condition(self.sender, self.object, self.body)}:\n" + \
                    f"{indent}{self._generate_action([self.stage_id, self.team_id, self.model_id, self.user_id], self.priority)}"

        self['generatedCode'] = condition

    @api.model
    def create(self, vals):
        res = super(AutomatedRules, self).create(vals)

        action = self.env['base.automation'].create({
            'name': res.name,
            'model_id': 156,
            'state': 'code',
            'trigger': 'on_create',
            'code': res.generatedCode.replace("\\n", ""),
        })
        res.action_id = action.id
        return res

    def unlink(self):
        self.action_id.unlink()
        return super(AutomatedRules, self).unlink()


    def write(self, vals_list):
        res = super(AutomatedRules, self).write(vals_list)
        if not self._context.get('is_code_up_to_date'):
            self.with_context(is_code_up_to_date=True).action_id.code = self.generatedCode.replace("\\n", "")
        return res
