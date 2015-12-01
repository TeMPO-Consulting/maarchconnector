(function() {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var filesubject = '';

    instance.web.Sidebar.include({

        redraw: function() {
            // method overloaded to manage the menu entry relative to Maarch
            var self = this;
            this._super.apply(this, arguments);
            self.$el.find('.oe_sidebar_add_attachment').after(QWeb.render('AddDocFromMaarch', {widget: self}))

            self.$el.find('.oe_sidebar_add_maarch_doc').on('click', function (e) {
                // TODO
            });
        },

        do_attachement_update: function(dataset, model_id, args) {
            // method overloaded to customize the display of error messages
            if(args && args[0].maarchError)
            {
                // display the error specific to Maarch
                this.do_notify('Connecteur Maarch', args[0].error, true); // true => "sticky"
                args = undefined;
            }
            this._super(dataset, model_id, args);
        },

        on_attachment_changed: function(e) {
            // method overloaded so that the user can specify the file subject (for Maarch)
            var _super = this._super.bind(this); // to use the right context
            instance.session.rpc('/tempo/maarchconnector/get_the_active_conf', {}).done(function (result) {
                if(result.is_conf_active)
                {
                    // if a Maarch conf is active, ask for the file subject in Maarch (by defaut : filename)
                    filesubject = prompt("Objet du document à enregistrer dans Maarch : ", e.target.value);
                    instance.session.rpc('/tempo/maarchconnector/set_subject', {
                        subject : filesubject
                    }).done(function (result) {
                        _super(e);
                    });
                } else {
                   _super(e);
                }
            });
        },

    });

})();
