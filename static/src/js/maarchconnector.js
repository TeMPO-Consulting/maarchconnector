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
        },

        /*
        on_attachment_changed: function(e) {
            filesubject = prompt("Objet du document dans Maarch : ");

            this._super(e);
        }
        */

    });

    // override here to add sthg after the add button is pressed
    /*
    instance.web.form.FieldBinary.include({

         on_file_change: function(e) {
            var self = this;
            var file_node = e.target;
            if ((this.useFileAPI && file_node.files.length) || (!this.useFileAPI && $(file_node).val() !== '')) {
                if (this.useFileAPI) {
                    var file = file_node.files[0];
                    if (file.size > this.max_upload_size) {
                        var msg = _t("The selected file exceed the maximum file size of %s.");
                        instance.webclient.notification.warn(_t("File upload"), _.str.sprintf(msg, instance.web.human_size(this.max_upload_size)));
                        return false;
                    }
                    var filereader = new FileReader();
                    filereader.readAsDataURL(file);
                    filereader.onloadend = function(upload) {
                        var data = upload.target.result;
                        data = data.split(',')[1];
                        self.on_file_uploaded(file.size, file.name, file.type, data);
                    };
                } else {
                    this.$el.find('form.oe_form_binary_form input[name=session_id]').val(this.session.session_id);
                    this.$el.find('form.oe_form_binary_form').submit();
                }

                // CODE ADDED HERE
                this.filesubject = prompt("Prompt test : ");

                this.$el.find('.oe_form_binary_progress').show();
                this.$el.find('.oe_form_binary').hide();
            }
        }

    });
    */

})();
