var AUFM = {
    UI: {
        initialize: function() {
            //setup all required materialize initializations.
            $(".dropdown-button").dropdown();
            $('.modal').modal();
        },
        CollectionCard: function() {

        },
        TableCard: function() {

        },
        Users: {
            _users: [],
    
        },
        Buildings: {
            _buildings: [],
    
        },
        Parts: {
            _building_id: undefined,
            _parts: [],
        },
        Protocols: {
            _part_id: undefined,
        },
    },
    Schema: {
        User: function(data) {},
        Building: function(data) {},
        Part: function(data) {},
        Protocol: function(data) {},
    },
};

$(document).ready(function(e) {
    AUFM.UI.initialize();
});