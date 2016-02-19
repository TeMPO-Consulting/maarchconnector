<?php

/*******************************************/
/***** CUSTOMIZED SEARCH WEBSERVICE *****/

// search criteria
$SOAP_typedef['searchDocumentsParams'] = array(
    'subject' => 'string',
    'min_doc_date' => 'string',
    'category' => 'string',
    'contact' => 'string',
);

// document details
$SOAP_typedef['item'] = array(
    'res_id' => 'long',
    'subject' => 'string',
    'doc_date' => 'date',
    'category' => 'string',
    'contact' => 'string',
);

// complex array: list of docs returned by the webservice
$SOAP_typedef['searchDocumentsResults'] = array(
    'item' => '{urn:MaarchSoapServer}item',
);

// function signature
$SOAP_dispatch_map['searchDocuments'] = array(
    'in' => array(
        'searchDocumentsParams' => '{urn:MaarchSoapServer}searchDocumentsParams',
    ),
    'out' => array(
        'out' => '{urn:MaarchSoapServer}searchDocumentsResults',
    ),
    'method' => "core#resources::searchDocuments",
);

