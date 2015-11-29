# -*- coding: utf-8 -*-

from openerp import models, fields, api


class Wizard(models.TransientModel):
    _name = 'maarchconnector.wizard'

    filesubject = fields.Char(string=u"Objet du document dans Maarch", required=True)

    @api.multi
    def get_filesubject(self):
        # TODO
        with open('/tmp/testlog.txt', 'a') as f:
            f.write("FILESUBJECT : %s\n" % self.filesubject)
        return self.filesubject


