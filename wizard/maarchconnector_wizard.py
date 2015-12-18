# -*- coding: utf-8 -*-

from openerp import models, fields, api, exceptions
from datetime import datetime
from datetime import date
from dateutil.relativedelta import relativedelta
from suds import TypeNotFound
import re


class SearchWizard(models.TransientModel):
    _name = 'maarch.search'

    filesubject = fields.Char(string=u"Objet du document / courrier", required=True)
    min_date = fields.Date(string=u"Daté à partir du", required=True,
                           default=datetime.now() - relativedelta(years=1))  # one year ago by default
    category = fields.Selection([('incoming', 'courrier arrivée'),
                                 ('outgoing', 'courrier départ'),
                                 ('internal', 'courrier interne')
                                 ], string='Catégorie')
    contact_name = fields.Char(string=u"Nom du contact")
    document_ids = fields.Many2many('maarch.document', string=u"Liste des documents")

    @api.multi
    def search_docs(self):
        """
        Display in the wizard the list of documents that match the criteria given by the user.
        Show a warning if the Maarch server isn't configured to use the search functionality.
        :return: a dictionary that corresponds to the wizard
        """
        try:
            maarch_client = self.env['maarchconnector.configuration'].get_maarch_client()
            param = maarch_client.factory.create('searchDocumentsParams')
            param.subject = self.filesubject
            param.min_doc_date = self.min_date
            if self.category:
                param.category = self.category
            else:
                param.category = None  # otherwise the category would be evaluated as False
            if self.contact_name:
                param.contact = self.contact_name
            else:
                param.contact = None
            response = maarch_client.service.searchDocuments(param)
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
                'res_model': 'maarch.search',
                'view_mode': 'form',
                'view_type': 'form',
                'res_id': self.id,  # reload the same wizard
                'views': [(False, 'form')],
                'target': 'new',
            }
        except TypeNotFound:
            # if the necessary changes haven't been done in the Maarch source code
            raise exceptions.ValidationError("Le serveur Maarch utilisé n'est pas configuré "
                                             "pour utiliser la recherche.")
        except Exception as e:
            # if a problem with the Maarch server occurs after the wizard has been displayed...
            raise exceptions.ValidationError(e.message)

    def _treeview_line_construction(self, doc, doclist):
        """
        Construct one line in the tree view
        :param doc: the document to add in the list
        :param doclist: the list used to populate the tree view
        """
        result = {}
        result.update({'maarch_id': doc.res_id})
        result.update({'subject': doc.subject.encode('utf8')})
        result.update({'doc_date': doc.doc_date})
        result.update({'category': self._get_category_designation(doc.category)})
        if doc.contact:
            result.update({'contact': doc.contact})
        else:
            result.update({'contact': '-'})
        doclist.append(result)

    def _get_category_designation(self, short_name):
        """
        Give the category designation that matches the short name in parameter
        :param short_name: the short category name
        :return: the complete designation
        """
        switcher = {
            'incoming': 'courrier arrivée',
            'outgoing': 'courrier départ',
            'internal': 'courrier interne',
        }
        return switcher.get(short_name, '-')

    @api.onchange('min_date')
    def _onchange_min_date(self):
        """
        Display a warning message when the selected date is in the future
        :return: a dictionary with a 'warning' key or None
        """
        if datetime.strptime(self.min_date, "%Y-%m-%d").date() > date.today():
            return {
                'warning': {
                    'title': "Date dans le futur",
                    'message': "La date sélectionnée est dans le futur.",
                },
            }

    @api.multi
    def add_maarchdoc_into_odoo(self):
        """
        Add the selected Maarch files into Odoo as attachments
        """
        IrAttachment = self.env['ir.attachment']
        try:
            maarch_client = self.env['maarchconnector.configuration'].get_maarch_client()
            for doc in self.document_ids:
                # get the data of all selected files
                if doc.to_add:
                    maarch_file = maarch_client.service.viewResource(doc.maarch_id, 'res_letterbox', 'adr_x', True)
                    binary_data = maarch_file.file_content
                    # add the file extension if necessary
                    if maarch_file.ext:
                        regex = '%s$' % maarch_file.ext
                        if not re.search(regex, doc.subject):
                            doc.subject = '%s.%s' % (doc.subject, maarch_file.ext)
                    file_data = {
                        'name': doc.subject,
                        'type': 'binary',
                        'datas': binary_data,
                        'datas_fname': doc.subject,
                        'res_model': self.env.context['model'],
                        'res_id': self.env.context['ids'][0],
                        'user_id': self.env.uid,
                    }
                    IrAttachment.create(file_data)
        except Exception as e:
            # if a problem with the Maarch server occurs after the wizard has been displayed...
            raise exceptions.ValidationError(e.message)


class DocumentWizard(models.TransientModel):
    _name = 'maarch.document'

    maarch_id = fields.Char(string=u"id", readonly=True)
    subject = fields.Char(string=u"objet")  # can be changed before recording
    doc_date = fields.Date(string=u"date", readonly=True)
    category = fields.Char(string=u"catégorie", readonly=True)
    contact = fields.Char(string=u"contact", readonly=True)
    to_add = fields.Boolean(string=u"à ajouter", default=False)

    @api.onchange('subject')
    def _onchange_subject(self):
        """
        Remove characters that can cause issues in filenames
        """
        invalid_characters = "<>:\"/\|?*"
        if self.subject:
            self.subject = ''.join(c for c in self.subject if c not in invalid_characters)
