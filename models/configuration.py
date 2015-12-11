# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
import re
import suds
import urllib2
from suds.client import Client


class Configuration(models.Model):

    _name = 'maarchconnector.configuration'

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
         "Le nom choisi doit être unique."),
    ]

    def _count_activated_configurations(self):
        """
        Get the number of active configurations
        :return: how many configurations are activated (integer)
        """
        request = "SELECT COUNT(activated) FROM maarchconnector_configuration WHERE activated IS TRUE;"
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
        nb_active_configurations = self._count_activated_configurations()
        for r in self:
            if r.activated and nb_active_configurations > 1:
                raise exceptions.ValidationError("Vous ne pouvez activer qu'un seul serveur Maarch à la fois.")

    @api.multi
    def get_the_active_configuration(self):
            """
            :return: the active configuration if it exists, otherwise None
            """
            ret = None
            configurations = self.search([('activated', '=', True)])
            if configurations:
                ret = configurations[0]
            return ret

    @api.onchange('activated')
    def _onchange_activated_configuration(self):
        """
        Display a warning message when no Maarch server is activated
        :return:
        """
        nb_active_configurations = self._count_activated_configurations()
        active_configuration = self.get_the_active_configuration()
        actual_record_id = self._origin.id

        # a warning message is displayed when "activated" isn't checked AND :
        # - either no other configuration was activated
        # - or the activated configuration was the one we're working on
        if (not self.activated) and \
            (nb_active_configurations == 0 or
                (active_configuration and active_configuration.id == actual_record_id)):
                    return {
                        'warning': {
                            'title': "Aucun serveur Maarch activé",
                            'message': "Les pièces jointes ne seront pas enregistrées dans Maarch "
                                       "si aucun serveur n'est activé.",
                        },
                    }

    @api.multi
    def configure_maarch_client(self):
        """
        Create and return the Maarch client to use. Raise an exception if the creation of the client fails.
        :return: a Maarch client
        """
        maarch_client = None
        error = ''
        active_conf = self.get_the_active_configuration()
        if active_conf:
            url_maarch = '%s/ws_server.php?WSDL' % active_conf.server_address
            user_maarch = active_conf.maarch_user_login
            password_maarch = active_conf.maarch_user_password
            try:
                maarch_client = Client(url_maarch, username=user_maarch, password=password_maarch)
            except urllib2.URLError:
                error = "accès au serveur impossible.<br/>L'adresse fournie est incorrecte, " \
                        "ou le serveur est indisponible."
            except suds.transport.TransportError:
                error = "connexion impossible.<br/>Vérifiez l'URL et les identifiants de connexion fournis."
            except Exception as e:
                error = e.message
            if error:
                raise Exception("Une erreur s'est produite lors du traitement avec Maarch&nbsp: %s" % error)
        return maarch_client




