/**
 * Routie library implemenation.
 */
AUFM.Routing = {
   setup: function() {
       routie({
           'buildings': function() {
               AUFM.UI.Breadcrumb.clear();
               AUFM.UI.Buildings.open();
           },
           'parts/:building_id': function(building_id) {
               building_id = parseInt(building_id);
               AUFM.UI.Buildings.close();
               var building = AUFM.UI.Buildings.buildings.find(b => {return b.id() == building_id});
               building = building ? building : building_id;
               AUFM.UI.Parts.open(building);
               AUFM.UI.Breadcrumb.navigate("Parts");
           },
           'protocols/:part_id': function(element_id) {
               element_id = parseInt(element_id);
               AUFM.UI.Parts.close();
               var part = AUFM.UI.Parts.parts.find(p => {return p.elementID() == element_id});
               if(!part) {
                   AUFM.Schema.Part.get(element_id, part => {
                       AUFM.UI.Protocols.open(part);
                   });
               } else
                   AUFM.UI.Protocols.open(part);
           },
           'protocol-families': function() {
               AUFM.UI.ProtocolFamilies.open();
           },
           'password-reset/:reset_token': function(reset_token) {
               AUFM.UI.PasswordReset.open(reset_token);
           },
       });
       // default
       if(window.location.hash == "" || window.location.hash == "#!")
           routie('buildings');
   },
};