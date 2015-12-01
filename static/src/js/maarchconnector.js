(function() {

    var instance = openerp;
    var _t = instance.web._t,
       _lt = instance.web._lt;
    var QWeb = instance.web.qweb;

    var filesubject = '';
    //var flagProcessOneFinished = false;
    //var flagProcessTwoFinished = false;

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
                //flagProcessOneFinished = true;
                //this._super(e); // "this" isn't bind to the right context...
            });

            // TODO : debug here
            /*
            // this._super(e) must be called once the subject is set
            while(!flagProcessTwoFinished)
            {
                if(!flagProcessOneFinished)
                {
                    sleep(30000);
                }
                else
                {
                    flagProcessTwoFinished = true;
                    this._super(e);
                }
            }
            */

            this._super(e);
        }

    });

    // wait for x milliseconds
    function sleep(milliseconds){
        var startTime = new Date().getTime();
        while (new Date().getTime() < startTime + milliseconds);
    }

})();
