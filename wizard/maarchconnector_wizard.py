# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Wizard(models.TransientModel):
    _name = 'maarchconnector.wizard'

    filesubject = fields.Char(string=u"Objet du document", required=True)

    @api.multi
    def search_files(self):
        # TODO
        pass

