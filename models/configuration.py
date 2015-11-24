# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import re

class Configuration(models.Model):

    _name = 'odoo_maarch.configuration'

    # "u" for unicode
    name = fields.Char(string=u"Nom", required=True)  # "name" required for search behaviors
    server_address = fields.Char(string=u"Adresse du serveur Maarch", required=True,
                                 help="L'URL de la racine du serveur Maarch")
    maarch_user_login = fields.Char(string=u"Identifiant de l'utilisateur Maarch", required=True)
    maarch_user_password = fields.Char(string=u"Mot de passe", required=True)
    activated = fields.Boolean(string=u"Activé", default=True)

    # check that the name is unique
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Le nom de la configuration doit être unique."),
    ]

    @api.constrains('server_address')
    def _server_address_format_validation(self):
        """
        Add "http://" to the server address if it hasn't been mentionned
        :return:
        """
        for r in self:
            if not re.search('^https?://', r.server_address):
                r.server_address = 'http://%s' % r.server_address




