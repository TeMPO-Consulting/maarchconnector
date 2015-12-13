# -*- coding: utf-8 -*-

import openerp.addons.web.http as http
from openerp.addons.web.controllers.main import Binary
from openerp.http import request
import base64
import simplejson
from datetime import datetime
from HTMLParser import HTMLParser
import os


class MaarchBinary(Binary):

    _filesubject_in_maarch = ''

    @http.route()
    def upload_attachment(self, callback, model, id, ufile):
        """
        Override the method of the Binary class.
        Check if the Maarch server configuration is OK and call the _add_to_maarch method.
        Display an appropriate message if the document can't be added into Maarch.
        :param callback
        :param model : model name
        :param id
        :param ufile : file that has to be added into Odoo and Maarch
        """
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        if self.is_conf_active().get('is_conf_active'):
            try:
                if not self._filesubject_in_maarch:
                    # if the user hasn't mentionned any subject we use the filename
                    if self._filesubject_in_maarch == "":
                        self._filesubject_in_maarch = ufile.filename
                    # if the user has clicked on "cancel" we abort the process
                    else:
                        args = {'error': "La pièce jointe n'a pas été enregistrée dans Maarch ni dans Odoo.",
                                'maarchError': True}
                        return out % (simplejson.dumps(callback), simplejson.dumps(args))
                # file extension without "."
                extension = os.path.splitext(ufile.filename)[1].replace('.', '')
                self._add_to_maarch(base64.encodestring(ufile.read()), self._filesubject_in_maarch, extension)
            except Exception as e:
                args = {'error': e.message, 'maarchError': True}
                return out % (simplejson.dumps(callback), simplejson.dumps(args))
            # get back to the beginning of the file
            ufile.seek(0)
        return super(MaarchBinary, self).upload_attachment(callback, model, id, ufile)

    @http.route('/tempo/maarchconnector/is_conf_active', type='json', auth='user')
    def is_conf_active(self):
        """
        Indicate if a Maarch configuration is active.
        """
        ret = False
        configuration_model = request.registry["maarchconnector.configuration"]
        if configuration_model.get_the_active_configuration(request.cr, request.uid, []):
            ret = True
        return {'is_conf_active': ret}

    @http.route('/tempo/maarchconnector/set_subject', type='json', auth='none')
    def set_subject(self, subject):
        """
        Set the subject for the file to be registered in Maarch (strip the XML and HTML tags)
        :param subject:
        :return:
        """
        mlstripper = MLStripper()
        mlstripper.feed(subject)
        self._filesubject_in_maarch = mlstripper.get_data()

    def get_client(self):
        """
        Call the method to create the Maarch client and return it.
        :return: the Maarch client
        """
        configuration_model = request.registry["maarchconnector.configuration"]
        return configuration_model.get_maarch_client(request.cr, request.uid, [])

    @http.route('/tempo/maarchconnector/is_client_ok', type='json', auth='user')
    def is_client_ok(self):
        """
        Check if the Maarch client can be created. If it fails, return a dictionary with an error.
        :return: a dictionary with an error (empty or not)
        """
        msg = ""
        try:
            self.get_client()
        except Exception as e:
            msg = e.message
        return {'error': msg}

    def _add_to_maarch(self, base64_encoded_content, document_subject, extension='pdf'):
        """
        Add the file into Maarch under the name "document_subject"
        :param base64_encoded_content: content of the file encoded in base 64
        :param document_subject: file name or subject
        :return:
        """
        maarch_client = self.get_client()
        today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # data relative to the document
        data = maarch_client.factory.create('arrayOfData')
        typist = maarch_client.factory.create('arrayOfDataContent')
        typist.column = 'typist'
        typist.value = 'odoo'
        typist.type = 'string'
        doc_date = maarch_client.factory.create('arrayOfDataContent')
        doc_date.column = 'doc_date'
        doc_date.value = today
        doc_date.type = 'string'
        type_id = maarch_client.factory.create('arrayOfDataContent')
        type_id.column = 'type_id'
        type_id.value = '15'  # misc. by default
        type_id.type = 'string'
        subject = maarch_client.factory.create('arrayOfDataContent')
        subject.column = 'subject'
        subject.value = document_subject.decode('utf8')
        subject.type = 'string'
        data.datas.append(typist)
        data.datas.append(doc_date)
        data.datas.append(type_id)
        data.datas.append(subject)
        if not extension:
            extension = 'pdf'
        # call to the web service method
        maarch_client.service.storeResource(base64_encoded_content, data, 'letterbox_coll',
                                            'res_letterbox', extension, 'INIT')


class MLStripper(HTMLParser):
    """
    Used to strip the XML and HTML tags
    """

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)
