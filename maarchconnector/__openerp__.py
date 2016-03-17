{
    'name': "TeMPO - Maarch Connector",
    'author': 'Julie Nuguet @ TeMPO Consulting',
    'version': '1.0',
    'depends': ['document'],
    'data': [
        'views/maarchconnector.xml',
        'views/maarchconnector_assets.xml',
        'wizard/maarchconnector_wizard_view.xml',
        'security/ir.model.access.csv',
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
