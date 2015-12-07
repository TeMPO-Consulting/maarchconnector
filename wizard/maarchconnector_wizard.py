# -*- coding: utf-8 -*-

from openerp import models, fields, api
from suds.client import Client


class Wizard(models.TransientModel):
    _name = 'maarchconnector.wizard'

    filesubject = fields.Char(string=u"Objet du document", required=True)

    @api.multi
    def search_files(self):
        # TODO : replace the test data
        _client_maarch = Client("http://10.0.0.195/maarch15/ws_server.php?WSDL", username="bblier", password="maarch")

        param = _client_maarch.factory.create('customizedSearchParams')
        param.subject = self.filesubject
        response = _client_maarch.service.customizedSearchResources(param)

        if response:
            docslist = response[0]
            with open('/tmp/testlog.txt', 'a') as f:
                for doc in docslist:
                    f.write("filesubject : %s\n" % doc.subject.encode('utf8'))

        return {
            'name': 'Recherche d\'un document dans Maarch',
            'type': 'ir.actions.act_window',
            'res_model': 'maarchconnector.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }

