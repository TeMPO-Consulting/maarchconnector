# -*- coding: utf-8 -*-

import openerp.addons.web.http as http
from openerp.addons.web.controllers.main import Binary
from openerp import exceptions
import base64
import simplejson
import suds
import urllib2
from suds.client import Client
from datetime import datetime

# test URL & user
_url_maarch = 'http://192.168.0.99/maarch15/ws_server.php?WSDL'
_user_maarch = 'bblier'
_password_maarch = 'maarch'

class MyBinary(Binary):

    @http.route()
    # @serialize_exception
    def upload_attachment(self, callback, model, id, ufile):
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        with open('/tmp/testlog.txt', 'a') as f:
            f.write("BEFORE : %s\n" % callback)
        try:
            self._add_to_maarch(base64.encodestring(ufile.read()), ufile.filename)
        except exceptions.ValidationError as e:
            args = {'error': str(e[1])}
            return out % (simplejson.dumps(callback), simplejson.dumps(args))
        with open('/tmp/testlog.txt', 'a') as f:
            f.write("AFTER : %s\n" % callback)
        # get back to the beginning of the file
        ufile.seek(0);
        return super(MyBinary, self).upload_attachment(callback, model, id, ufile)

    def _add_to_maarch(self, base64_encoded_content, document_subject):
        """
        Add the file into Maarch under the name "document_subject"
        :param base64_encoded_content: content of the file encoded in base 64
        :param document_subject: file name
        :return:
        """
        try:
            _client_maarch = Client(_url_maarch, username=_user_maarch, password=_password_maarch)
            error = ''
            mydate = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # data relative to the document
            data = _client_maarch.factory.create('arrayOfData')
            typist = _client_maarch.factory.create('arrayOfDataContent')
            typist.column = 'typist'
            typist.value = 'odoo'
            typist.type = 'string'
            doc_date = _client_maarch.factory.create('arrayOfDataContent')
            doc_date.column = 'doc_date'
            doc_date.value = mydate
            doc_date.type = 'string'
            type_id = _client_maarch.factory.create('arrayOfDataContent')
            type_id.column = 'type_id'
            type_id.value = '15'  # misc. by default
            type_id.type = 'string'
            subject = _client_maarch.factory.create('arrayOfDataContent')
            subject.column = 'subject'
            subject.value = document_subject.decode('utf8')
            subject.type = 'string'
            data.datas.append(typist)
            data.datas.append(doc_date)
            data.datas.append(type_id)
            data.datas.append(subject)
            # call to the web service method
            _client_maarch.service.storeResource(base64_encoded_content, data, 'letterbox_coll', 'res_letterbox', 'pdf', 'INIT')
        except urllib2.URLError:
            error = "l'URL de connexion est incorrecte, ou le serveur est indisponible."
        except suds.transport.TransportError:
            error = "les identifiants de connexion fournis sont incorrects."
        except:
            error = "une erreur est survenue lors du traitement."
        if error:
            raise exceptions.ValidationError("La pièce jointe ne peut pas être enregistrée dans Maarch : %s" % error)

