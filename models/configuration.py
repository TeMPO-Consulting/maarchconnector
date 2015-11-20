# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions

class Configuration(models.Model):

    _name = 'odoo_maarch.configuration'

    # "u" for unicode
    name = fields.Char(string=u"Nom", required=True)  # "name" required for search behaviors
    server_address = fields.Char(string=u"Adresse du serveur Maarch", required=True,
                                 help="L'URL de la racine du serveur Maarch")
    maarch_user_login = fields.Char(string=u"Identifiant de l'utilisateur Maarch", required=True)
    maarch_user_password = fields.Char(string=u"Mot de passe", required=True)

    # verification constraint (SQL)
    _sql_constraints = [
        ('name_unique',
         'UNIQUE(name)',
         "Le nom de la configuration doit être unique."),
    ]

    # verification constraint (Python)
    # TODO
    """
    @api.constrains('name', 'server_address', 'maarch_user_id', 'maarch_user_password')
    def _check_instructor_not_in_attendees(self):
        for r in self:
            if ....:
                raise exceptions.ValidationError("Format invalide")
    """




