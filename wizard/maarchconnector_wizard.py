# -*- coding: utf-8 -*-

from openerp import models, fields, api
from suds.client import Client


class Wizard(models.TransientModel):
    _name = 'maarch.wizard'

    filesubject = fields.Char(string=u"Objet du document / courrier", required=True)
    document_ids = fields.Many2many('maarch.document', string=u"Liste des documents")

    @api.multi
    def search_docs(self):
        # TODO : replace the test data
        _client_maarch = Client("http://10.0.0.195/maarch15/ws_server.php?WSDL", username="bblier", password="maarch")
        param = _client_maarch.factory.create('customizedSearchParams')
        param.subject = self.filesubject
        response = _client_maarch.service.customizedSearchResources(param)
        self.document_ids = None  # empty the result list in case the wizard has been reloaded
        doclist = []
        if response:
            maarchdoc = response[0]
            # if there is more than 1 result we handle a list
            if isinstance(maarchdoc, list):
                for doc in maarchdoc:
                    self._treeview_line_construction(doc, doclist)
            # if there is exactly one result we get directly the document instance
            else:
                self._treeview_line_construction(maarchdoc, doclist)
        self.document_ids = doclist
        return {
            'name': 'Recherche d\'un document dans Maarch',
            'type': 'ir.actions.act_window',
            'res_model': 'maarch.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,  # reload the same wizard
            'views': [(False, 'form')],
            'target': 'new',
        }

    def _treeview_line_construction(self, doc, doclist):
        """
        Construct one line in the tree view
        :param doc: the document to add in the list
        :param doclist: the list used to populate the tree view
        :return:
        """
        result = {}
        result.update({'maarch_id': doc.res_id})
        result.update({'subject': doc.subject.encode('utf8')})
        result.update({'doc_date': doc.doc_date})
        doclist.append(result)

    @api.multi
    def add_maarchdoc_into_odoo(self):
        # TODO
        pass


class DocumentWizard(models.TransientModel):
    _name = 'maarch.document'

    maarch_id = fields.Char(string=u"id", readonly=True)
    subject = fields.Char(string=u"objet", readonly=True)
    doc_date = fields.Date(string=u"date", readonly=True)
    to_add = fields.Boolean(string=u"à ajouter", default=False)
