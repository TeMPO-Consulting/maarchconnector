# -*- coding: utf-8 -*-

from openerp import models, fields, api
from suds.client import Client


class Wizard(models.TransientModel):
    _name = 'maarch.wizard'

    filesubject = fields.Char(string=u"Objet du document", required=True)
    document_ids = fields.One2many('maarch.document', 'document_id', string=u"Documents")

    @api.multi
    def validate(self):
        # TODO
        """
        return {
            'name': 'Recherche d\'un document dans Maarch',
            'type': 'ir.actions.act_window',
            'res_model': 'maarch.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            # 'res_id': this.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        """

    @api.onchange('filesubject')
    # @api.constrains('filesubject')
    def on_filesubject_change(self):

        # TODO : replace the test data
        _client_maarch = Client("http://10.0.0.195/maarch15/ws_server.php?WSDL", username="bblier", password="maarch")

        param = _client_maarch.factory.create('customizedSearchParams')
        param.subject = self.filesubject
        response = _client_maarch.service.customizedSearchResources(param)
        final_docs_list = []
        if response:
            docslist = response[0]
            for doc in docslist:
                result = {}
                result.update({'maarch_id': doc.res_id})
                result.update({'subject': doc.subject.encode('utf8')})
                final_docs_list.append(result)
            with open('/tmp/testlog.txt', 'a') as f:
                f.write("final_docs_list : %s\n" % final_docs_list)
        self.document_ids = final_docs_list


class DocumentWizard(models.TransientModel):
    _name = 'maarch.document'

    maarch_id = fields.Char(string="id", readonly=True)
    subject = fields.Char(string=u"Objet", readonly=True)
    document_id = fields.Many2one('maarch.wizard')

