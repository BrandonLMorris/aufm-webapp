var AUFM = {
    /*
     * An collection of UI specific utilities and managing the 
     *  data that should be binded with these UI elements.
     */
    UI: {
        initialize: function() {
            //setup all required materialize initializations.
            $(".dropdown-button").dropdown();
            $('.modal').modal();

            AUFM.UI.Cards.setupCards();
            AUFM.UI.Buildings.open();
        },
        Cards: {
            templates: {
                card: undefined,
                collection: '<ul class="collection"></ul>',
                collection_item: undefined,
                property_container: undefined,
                property_row: undefined,
            },
            setupCards: function() {
                // set templates.
                this.templates.card = $('#card_template').html();
                this.templates.collection_item = $('#collection_item_template').html();
                this.templates.property_container = $('#property_container_template').html();
                this.templates.property_row = $('#property_row_template').html();

                AUFM.UI.Buildings.card = this.create(AUFM.UI.Buildings.card_options);
                AUFM.UI.Parts.card = this.create(AUFM.UI.Parts.card_options);
            },
            create: function(options) {
                var self = this;
                var card = $(this.templates.card);
                if(options.id == undefined)
                    throw "Missing required parameter 'id' for card.";
                else 
                    card.attr("id", options.id);

                // Card title.
                if(options.title)
                    card.find('.card-title').html(options.title);
                
                // Setting up searching through content.
                if(options.search) {
                    card.find('.search-input input').attr("id", options.id + "_search").change(function(e) {
                        var value = $(this).val().toLowerCase().trim();
                        if(value == "")
                            card.find('.collection-item').show();
                        else
                            card.find('.collection-item').each(i => {
                                if(!i.html().toLowerCase().contains(value))
                                    i.hide();
                            });
                    });
                    card.find('.search-input label').attr("for", options.id + "_search").html("Search " + options.title + "...");
                    // setup search actions.
                } else
                    card.find('.search').hide();

                /**
                 * The card content area.
                 *  Properties defines a table of key, value properties.
                 *  Collection defines a single list of collections with actions.
                 *  Content defines a set of markup or text that is set to the content area.
                 */
                var content = card.find('.content-container');
                if(options.properties) {

                } else if(options.collection) {
                    content.html(this.templates.collection);
                    card.populate = function(collection) {
                        card.collection = collection;
                        content.find('.collection').html(
                            card.collection.reduce(function(str, item) {
                                if(!item.collection)
                                    return str;
                                return str + AUFM.Util.template(self.templates.collection_item, item.collection());
                            }, "")
                        );
                        content.find('.collection-item').click(function(e) {
                            var id = $(this).data("id");
                            var item = collection.find((c) => { return c.id() == id; });
                            options.collection(item);
                            e.stopPropagation();
                            e.preventDefault();
                        });
                    };
                } else if(options.content)
                    content.html(options.content);
                else
                    throw "Invalid card content.";

                if(options.actions) {
                    card.find('.card-action .btn').html(options.actions.title);
                } else 
                    card.find('.card-actions').hide();

                $('#content_area').append(card);
                return card;
            },
        },
        Users: {
            _users: [],
            card: undefined,
        },
        Buildings: {
            _buildings: [],
            card_options: {
                id: "building_card",
                title: "Buildings",
                search: true,
                collection: function(building) {
                    AUFM.UI.Buildings.close();
                    AUFM.UI.Parts.open(building);
                },
                actions: {
                    title: "Add Building",
                    click: function(e) {
                        // trigger add building modal
                    },
                },
            },
            card: undefined,
            open: function() {
                var self = this;
                AUFM.Util.api({
                    url: "building",
                    callback: function(data) {
                        data.forEach(function(b) {
                            self._buildings.push(new AUFM.Schema.Building(b));
                        });
                        self.card.populate(self._buildings);
                        self.card.fadeIn();
                    },
                });
            },
            close: function() {
                this.card.hide();
            },
        },
        Parts: {
            _building: undefined,
            _parts: [],
            card_options: {
                id: "parts_card",
                title: "Parts",
                collection: function(part) {
                    AUFM.UI.Parts.close();
                    AUFM.UI.Prtocols.open(part);
                },
                actions: {
                    title: "Add New Part",
                    click: function(e) {
                        // trigger add building modal
                    },
                },
            },
            card: undefined,
            open: function(building) {
                this._building = building;
                var self = this;
                AUFM.Util.api({
                    url: "building/" + self._building.id() + "/part",
                    callback: function(data) {
                        data.parts.forEach(function(p) {
                            self._parts.push(new AUFM.Schema.Part(p));
                        });
                        self.card.populate(self._parts);
                        self.card.fadeIn();
                    },
                });
            },
            close: function() {
                this.card.fadeOut();
            },
        },
        Protocols: {
            _part: undefined,
            _protocols: [],
        },
    },
    /**
     * Javascript Class representations of the database schema,
     *  with added functionality for interacting with the database.
     */
    Schema: {
        User: function(data) {
            this._user_id = parseInt(data.user_id);
            this._first_name = data.first_name;
            this._last_name = data.last_name;
            this._email = data._email;
            this._permissions = parseInt(data.permissions);

            this.id = function() {
                return this._user_id;
            };

            this.collection = function() {
                return {
                    id: this._user_id,
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
                    name: this._name,
                };
            };
        },
        Part: function(data) {
            this._part_id = parseInt(data.part_id);
            this._element_id = parseInt(data.element_id);
            this._building_id = parseInt(data.building_id);

            this.id = function() {
                return this._part_id;
            };

            this.collection = function() {
                return {
                    id: this._part_id,
                    name: this._element_id,
                };
            };
        },
        Protocol: function(data) {
            this._protocol_id = parseInt(data.protocol_id);
            this.value = data.value;

            this.id = function() {
                return this._protocol_id;
            };
        },
    },
    Util: {
        template: function(template, data) {
            template = $.trim(template);
            return template.replace(/%(\w*)%/g, function (m, key) {
                return data.hasOwnProperty(key) ? data[key] : "";
            });
        },
        api: function(params) {
            $.ajax({
                url: window.location.origin + "/api/" + params.url,
                type: params.type ? params.type : "GET",
                success: params.callback,
                error: function(jqXHR, text, error) {
                    params.callback({
                        error: text + " " + error,
                    });
                },
            });
        },
    },
};

$(document).ready(function(e) {
    AUFM.UI.initialize();
});