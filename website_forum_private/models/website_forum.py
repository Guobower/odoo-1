# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Forum(models.Model):
    _inherit = 'forum.forum'

    security_type = fields.Selection([('public', 'Public'), ('private', 'Private')], required=True, default='private')
    group_ids = fields.Many2many('res.groups', string="Authorized Groups")
