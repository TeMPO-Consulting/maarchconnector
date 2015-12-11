# -*- coding: utf-8 -*-

import openerp.addons.web.http as http
from openerp.addons.web.controllers.main import Binary
from openerp import exceptions
from openerp.http import request
import base64
import simplejson
import suds
import urllib2
from suds.client import Client
from datetime import datetime
import os


class MyBinary(Binary):

    _client_maarch = None
    _filesubject_in_maarch = ''

    @http.route()
    def upload_attachment(self, callback, model, id, ufile):
        """
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
            except exceptions.ValidationError as e:
                args = {'error': str(e[1]), 'maarchError': True}
                return out % (simplejson.dumps(callback), simplejson.dumps(args))
            # get back to the beginning of the file
            ufile.seek(0)
        return super(MyBinary, self).upload_attachment(callback, model, id, ufile)

    @http.route('/tempo/maarchconnector/get_the_active_conf', type='json', auth='user')
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
        Set the subject for the file to be registered in Maarch
        :param subject:
        :return:
        """
        self._filesubject_in_maarch = subject

    @http.route('/tempo/maarchconnector/client_creation', type='json', auth='user')
    def client_creation(self, call_from_js=False):
        self._client_maarch = None
        error = ''
        configuration_model = request.registry["maarchconnector.configuration"]
        active_conf = configuration_model.get_the_active_configuration(request.cr, request.uid, [])
        if active_conf:
            url_maarch = '%s/ws_server.php?WSDL' % active_conf.server_address
            user_maarch = active_conf.maarch_user_login
            password_maarch = active_conf.maarch_user_password
            try:
                self._client_maarch = Client(url_maarch, username=user_maarch, password=password_maarch)
            except urllib2.URLError:
                error = "accès au serveur impossible.<br/>L'adresse fournie est incorrecte, " \
                        "ou le serveur est indisponible."
            except suds.transport.TransportError:
                error = "connexion impossible.<br/>Vérifiez l'URL et les identifiants de connexion fournis."
            except Exception as e:
                error = e.message
            if error:
                error = "Une erreur s'est produite lors du traitement avec Maarch&nbsp: %s" % error
                if call_from_js:
                    return {'error': error}  # if the method is called from the JS part
                else:
                    raise exceptions.ValidationError(error)  # if the method is called from the Python part

    def _add_to_maarch(self, base64_encoded_content, document_subject, extension='pdf'):
        """
        Add the file into Maarch under the name "document_subject"
        :param base64_encoded_content: content of the file encoded in base 64
        :param document_subject: file name or subject
        :return:
        """
        self.client_creation()
        mydate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        # data relative to the document
        data = self._client_maarch.factory.create('arrayOfData')
        typist = self._client_maarch.factory.create('arrayOfDataContent')
        typist.column = 'typist'
        typist.value = 'odoo'
        typist.type = 'string'
        doc_date = self._client_maarch.factory.create('arrayOfDataContent')
        doc_date.column = 'doc_date'
        doc_date.value = mydate
        doc_date.type = 'string'
        type_id = self._client_maarch.factory.create('arrayOfDataContent')
        type_id.column = 'type_id'
        type_id.value = '15'  # misc. by default
        type_id.type = 'string'
        subject = self._client_maarch.factory.create('arrayOfDataContent')
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
        self._client_maarch.service.storeResource(base64_encoded_content, data, 'letterbox_coll',
                                                  'res_letterbox', extension, 'INIT')

