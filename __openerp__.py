{
    'name': "Module d'interface avec Maarch",
    'depends': ['document'],
    'data': [
        'views/maarchconnector.xml',
        'views/maarchconnector_assets.xml',
    ],
    'js': [
        'static/src/js/maarchconnector.js'
    ],
    'qweb': [
        'static/src/xml/maarchconnector.xml'
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
