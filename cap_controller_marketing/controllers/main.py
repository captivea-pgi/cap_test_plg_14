import base64
from odoo import _, exceptions, http, tools
from odoo.http import request
from werkzeug.exceptions import BadRequest
from odoo.tools import consteq
from odoo.addons.mass_mailing.controllers.main import MassMailController
from werkzeug.urls import url_encode

import logging

_logger = logging.getLogger(__name__)

class CapMassMailController(http.Controller):

    @http.route(['/mail/mailing/<int:mailing_id>/unsubscribe'], type='http', website=True, auth='public')
    def mailing(self, mailing_id, email=None, res_id=None, token="", **post):
        _logger.info("WE ARE IN MAILING OVERRIDEN")
        return super(CapMassMailController, self).mailing(mailing_id, email=None, res_id=None, token="", **post)