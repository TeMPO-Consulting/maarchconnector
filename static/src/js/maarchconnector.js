(function() {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var filesubject = '';

    instance.web.Sidebar.include({

        redraw: function() {
            // method overriden to manage the menu entry relative to Maarch
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('AddDocFromMaarch', {widget: self}))

            self.$el.find('.oe_sidebar_add_maarch_doc').on('click', function (e) {
                self.on_maarch_doc();
            });
        },

        do_attachement_update: function(dataset, model_id, args) {
            // method overriden to customize the display of error messages
            if(args && args[0].maarchError)
            {
                // display the error specific to Maarch
                this.do_notify('Connecteur Maarch', args[0].error, true); // true => "sticky"
                args = undefined;
            }
            this._super(dataset, model_id, args);
        },

        on_attachment_changed: function(e) {
            // method overriden so that the user can specify the file subject (for Maarch)
            var self = this;
            var _super = this._super.bind(this); // to use the right context
            instance.session.rpc('/tempo/maarchconnector/is_conf_active', {}).done(function (result) {
                if(result.is_conf_active)
                {
                    // if a configuration is active: try to create the Maarch client
                    instance.session.rpc('/tempo/maarchconnector/client_creation', {
                        call_from_js : true
                    }).done(function (result) {
                        if(result && result.error && result.error.length > 0)
                        {
                            self.do_notify('Connecteur Maarch', result.error, true);
                        }
                        else
                        {
                            // ask for the file subject in Maarch (by defaut: filename)
                            filesubject = prompt("Objet du document à enregistrer dans Maarch : ", e.target.value);
                            instance.session.rpc('/tempo/maarchconnector/set_subject', {
                                subject : filesubject
                            }).done(function (result) {
                                _super(e);
                            });
                        }
                    });
                } else {
                    // if no configuration is active: the attachment is added only into Odoo
                    _super(e);
                }
            });
        },

        on_maarch_doc: function() {
            // method called on click on "Add from Maarch..."
            var self = this;

            instance.session.rpc('/tempo/maarchconnector/is_conf_active', {}).done(function (result) {
                if(!result.is_conf_active)
                {
                    // if no configuration is active: display an error message
                    self.do_notify('Connecteur Maarch',
                                   'Erreur : aucun serveur Maarch n\'est activé.<br>' +
                                   'Veuillez choisir le serveur à utiliser via le menu "Connecteur Maarch".', true);
                }
                else
                {
                    instance.session.rpc('/tempo/maarchconnector/client_creation', {
                        call_from_js : true
                    }).done(function (result) {
                        if(result && result.error && result.error.length > 0)
                        {
                            // if the creation of the Maarch client has failed: display an error message
                            self.do_notify('Connecteur Maarch', result.error, true);
                        }
                        else
                        {
                            // if the connection with Maarch is OK: display a wizard to search a document to add
                            var view = self.getParent();
                            var ids = (view.fields_view.type != "form") ? view.groups.get_selection().ids : [view.datarecord.id];
                            var context = {
                                'model': view.dataset.model,
                                'ids': ids,
                            };

                            // used to send data to the "do_action" method
                            var action = {
                                name: "Recherche d'un document dans Maarch",
                                type: 'ir.actions.act_window',
                                res_model: 'maarch.wizard',
                                view_mode: 'form',
                                view_type: 'form',
                                views: [[false, 'form']],
                                target: 'new',
                                context: context,
                            };
                            // used to open the new view
                            self.do_action(action, {
                                // the list of attachments is refreshed when the wizard is closed
                                on_close: function () {
                                    self.do_attachement_update(self.dataset, self.model_id);
                                }
                            });
                        }
                    });
                }
            });
        }
    });

})();
