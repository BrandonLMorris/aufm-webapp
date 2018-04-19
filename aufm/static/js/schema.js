/**
 * Javascript Class representations of the database schema,
 *  with added functionality for interacting with the database.
 */
AUFM.Schema = {
    User: function(data) {
        this._id = parseInt(data.id);
        this._first_name = data.first_name;
        this._last_name = data.last_name;
        this._email = data.email;
        this._permissions = parseInt(data.permissions);

        this.id = function() {
            return this._id;
        };

        this.collection = function() {
            return {
                id: this._id,
                name: this._first_name + " " + this._last_name,
            };
        };
    },
    Building: function(data) {
        this._building_id = parseInt(data.building_id);
        this._name = data.name;

        this.id = function() {
            return this._building_id;
        };

        this.collection = function() {
            return {
                id: this._building_id,
                value: this._name,
            };
        };
        this.remove = function(callback) {
            var self = this;
            AUFM.Util.api({
                url: "building/" + self.id(),
                type: "DELETE",
                callback: callback,
            });
        };
    },
    Part: function(data) {
        this._part_id = parseInt(data.part_id);
        this._element_id = parseInt(data.element_id);
        this._part_name = data.part_name;
        this._building_id = parseInt(data.building_id);

        this.id = function() {
            return this._part_id;
        };

        this.elementID = function() {
            return this._element_id;
        };

        this.name = function() {
            return this._part_name;
        };

        this.collection = function() {
            return {
                id: this._part_id,
                value: (this._part_name === null ? "[No Name]" : this._part_name) + " (ID " +this._element_id + ")",
            };
        };
        this.remove = function(callback) {
            var self = this;
            AUFM.Util.api({
                url: "part/" + self.elementID(),
                type: "DELETE",
                callback: callback,
            });
        };
    },
    Protocol: function(data) {
        this._protocol_id = parseInt(data.protocol_id);
        this._value = data.value;

        this.id = function() {
            return this._protocol_id;
        };

        this.collection = function() {
            return {
                id: this._protocol_id,
                value: this._value,
            };
        };
        this.remove = function(callback) {
            var self = this;
            AUFM.Util.api({
                url: "part/" + AUFM.UI.Protocols.part.elementID() + "/protocol/" + self.id(),
                type: "DELETE",
                callback: callback,
            });
        };
    },
    ProtocolFamily: function(data) {
        this._family_id = parseInt(data.family_id);
        this._family_name = data.family_name;

        this.id = function() {
            return this._family_id;
        };

        this.collection = function() {
            return {
                id: this._family_id,
                value: this._family_name,
            };
        };
        this.remove = function(callback) {
            var self = this;
            AUFM.Util.api({
                url: "protocol-family/" + self.id(),
                type: "DELETE",
                callback: callback,
            });
        };
        this.removeProtocol = function(toRemove, callback) {
            var self = this;
            AUFM.Util.api({
                url: 'protocol-family/' + self.id() + '/protocol/' + toRemove.id(),
                type: "DELETE",
                callback: callback,
            });
        };
    },
    setup: function() {
        this.Building.get = function(id, callback) {
            AUFM.Util.api({
                url: "building/" + id,
                callback: function(data) {
                    callback(new AUFM.Schema.Building(data));
                },
            });
        };
        this.Part.get = function(element_id, callback) {
            AUFM.Util.api({
                url: "part/" + element_id,
                callback: function(data) {
                    callback(new AUFM.Schema.Part(data));
                },
            });
        };
    },
};