Odoo module - interface with Maarch

To make this module work with the 1.5 version of Maarch, the following code must be added into the Maarch source code:

=> the content of misc/customized_ws.php must be added in the file:
   MAARCH_ROOT/core/class/ws.php

=> the content of misc/customized_resources_controler.php must be added in the file:
   MAARCH_ROOT/core/class/resources_controler.php
in the "resources_controler" class.
