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

    def _count_activated_configuration(self):
        """
        Get the number of active configurations
        :return: how many configurations are activated (integer)
        """
        request = "SELECT COUNT(activated) FROM odoo_maarch_configuration WHERE activated IS TRUE;"
        self.env.cr.execute(request)
        result = self.env.cr.fetchone()
        # convert the tuple "result" into an integer
        return int(''.join(str(x) for x in result))

    @api.constrains('server_address')
    def _validate_server_address_format(self):
        """
        Add "http://" to the server address if it hasn't been mentionned
        :return:
        """
        for r in self:
            if not re.search('^https?://', r.server_address):
                r.server_address = 'http://%s' % r.server_address

    @api.constrains('activated')
    def _validate_active_configuration(self):
        """
        Checks that there is no more than one configuration active
        :return:
        """
        # number of active configurations included the one we're working on
        active_configurations = self._count_activated_configuration()
        for r in self:
            if r.activated and active_configurations > 1:
                raise exceptions.ValidationError("Vous ne pouvez activer qu'une seule configuration à la fois.")

    def get_the_active_configuration(self):
            """
            :return: the active configuration if it exists, otherwise None
            """
            ret = None
            configurations = self.search([('activated', '=', True)])
            if configurations:
                ret = configurations[0]
            return ret



