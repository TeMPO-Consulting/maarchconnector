Odoo module - interface with Maarch

To make this module work with the 1.5 version of Maarch:

1) the following code must be added into the Maarch source code:

=> the content of misc/customized_ws.php must be added in the file:  
   MAARCH_ROOT/core/class/ws.php

=> the content of misc/customized_resources_controler.php must be added in the file:  
   MAARCH_ROOT/core/class/resources_controler.php  
in the "resources_controler" class.


2) A new basket (OdooBasket) must be created for the letterbox collection with the following filter:  
status = 'INIT' AND typist = 'odoo'

The filter on the InitBasket must be modified as follows:  
status = 'INIT' AND typist != 'odoo'
