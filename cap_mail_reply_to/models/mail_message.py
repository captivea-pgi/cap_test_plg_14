# coding: utf-8

from odoo import api, models, fields
from odoo.exceptions import UserError
#import logging
from odoo.tools.translate import _
from datetime import datetime

models_to_check = ['helpdesk.ticket']
#_logger = logging.getLogger(__name__)

class CapMailMessage(models.Model):
    _inherit = 'mail.message'

    @api.model
    def create(self, values):
        '''
        ATTENTION : inherit create method may impact the server performance
        Create and write methods have recurrent call on Odoo it means the code inside this function will be
        called a lot of times. (poor english :s)
        :param values:
        :return:
        '''
        message = super(CapMailMessage, self).create(values)
        
        if message.model in models_to_check and message.message_type == 'notification':
            #Link between the helpdesk.ticket model and the message's id
            linked_object = self.env[message.model].sudo().search([('id', '=', message.res_id)])
                
            #check which contact is linked to the ticket
            contact = linked_object.partner_id if linked_object.partner_id else ''

            #Find the right email to reply to
            if contact:
                # raise UserError(contact.company_id)
                email = "sales@cargobikedistribution.com" if contact.company_id.id == 1 else "info@yubabikes.com"
            else:
                email = "info@yubabikes.com"

            #Amend the value of reply_to with the email
            message.write({'reply_to': email})

        return message