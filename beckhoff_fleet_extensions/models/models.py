# -*- coding: utf-8 -*-

from odoo import models, fields, api

class BeckhoffFleet(models.Model):
    _inherit ='fleet.vehicle'

    fuel_pin = fields.Char(string="Tank-Pin", help="Feld für den PIN der Tankkarte")

class BeckhoffFleetVehicleService(models.Model):
    _inherit = 'fleet.vehicle.log.services'

    bitfarm_id = fields.Char(string="Bitfarm-Rechnung", help="GDocID der Rechnung in der Bitfarm.")
