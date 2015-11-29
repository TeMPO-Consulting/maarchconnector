(function() {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    instance.web.Sidebar.include({

        do_attachement_update: function(dataset, model_id, args) {
            if(args && args[0].maarchError)
            {
                // display the error specific to Maarch
                this.do_notify('Connecteur Maarch', args[0].error, true); // true => "sticky"
                args = undefined;
            }
            this._super(dataset, model_id, args);
        }

    });

})();