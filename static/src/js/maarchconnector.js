(function() {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var filesubject = ''

    instance.web.Sidebar.include({

        do_attachement_update: function(dataset, model_id, args) {
            if(args && args[0].maarchError)
            {
                // display the error specific to Maarch
                this.do_notify('Connecteur Maarch', args[0].error, true); // true => "sticky"
                args = undefined;
            }
            this._super(dataset, model_id, args);
        },

        on_attachment_changed: function(e) {
            instance.session.rpc('/tempo/maarchconnector/get_the_active_conf', {
            }).done(function (result) {
                if(result.is_conf_active)
                {
                    // if a Maarch conf is active, ask for the file subject in Maarch (by defaut : filename)
                    filesubject = prompt("Objet du document à enregistrer dans Maarch : ", e.target.value);
                    instance.session.rpc('/tempo/maarchconnector/set_subject', {
                        subject : filesubject
                    });
                }
            });

            this._super(e);
        }

    });

})();
