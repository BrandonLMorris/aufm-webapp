var AUFM = {
    Constants: {
        DEFAULT_COLOR: "blue darken-4",
        DEFAULT_FONT_COLOR: "" // blank = default materialize
    },
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
        /*
         * Cards are dynamically created by passing in a set
         *  of options that define how the card will look and behave.
         */
        Cards: {
            templates: {
                card: undefined,
                collection: '<ul class="collection"></ul>',
                collection_item: undefined,
                collapsible: '<ul class="collapsible" data-collapsible="accordion">/<ul>',
                collapsible_item: undefined,
                property_container: undefined,
                property_row: undefined,
            },
            setupCards: function() {
                // set templates.
                this.templates.card = $('#card_template').html();
                this.templates.collection_item = $('#collection_item_template').html();
                this.templates.collapsible_item = $('#collapsible_item_template').html();
                this.templates.property_container = $('#property_container_template').html();
                this.templates.property_row = $('#property_row_template').html();

                // build cards.
                AUFM.UI.Buildings.card = this.create(AUFM.UI.Buildings.card_options);
                AUFM.UI.Parts.card = this.create(AUFM.UI.Parts.card_options);
                AUFM.UI.Protocols.card = this.create(AUFM.UI.Protocols.card_options);
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
                    card.find('.search-input input').attr("id", options.id + "_search").on('input', function(e) {
                        var value = $(this).val().toLowerCase().trim();
                        if(value == "")
                            card.find('.collection-item').show();
                        else
                            card.find('.collection-item').each(function(index) {
                                var ele = $(this);
                                if(!ele.html().toLowerCase().includes(value))
                                    ele.hide();
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
                    content.html(this.templates.property_container);
                    card.populate = function(properties) {
                        card.properties = properties;
                        /*card.find('.property-table').append(
                            card.properties.reduce(function(str, item) {
                                return str;
                            }, "");
                        );*/
                    };
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
                } else if(options.collapsible) {
                    content.html(this.templates.collapsible);
                    card.populate = function(collection) {
                        card.collection = collection;
                        content.find('.collapsible').html(
                            card.collection.reduce(function(str, item) {
                                if(!item.collection)
                                    return str;
                                return str + AUFM.Util.template(self.templates.collapsible_item, item.collection());
                            }, "")
                        );
                        content.find('.collapsible').collapsible();
                    };
                } else if(options.content)
                    content.html(options.content);
                else
                    throw "Invalid card content.";

                if(options.actions) {
                    card.find('.card-action .btn').html(options.actions.title).click(function(e) {
                        options.actions.click(e);
                    });
                } else 
                    card.find('.card-actions').hide();

                $('#content_area').append(card);
                return card;
            },
        },
        /**
         * Modals are similar to cards in terms of creation, but are meant to
         *  complete a specific task and notify the caller when that task is 
         *  either completed or cancelled.
         */
        Modals: {
            open: function(options) {
                var template = this.templates[options.template];
                if(!template)
                    throw "No template was given for the modal.";
                if(!template.id)
                    throw "id parameter in template is required for modal.";
                var modal = $('#' + template.id);
                if(modal.length <= 0) {
                    modal = $($('#modal_template').html());
                    modal.attr("id", template.id);
                    $('body').append(modal);
                    modal.modal();
                }
                modal.item = options.item;
                options.context = options.context ? options.context : "create";
                modal.context = options.context;
                if(template.title) {
                    var title = typeof template.title === "string" ? template.title : template.title[options.context];
                    modal.find('.modal-content h4').html(title);
                }
                if(template.content)
                    modal.find('.modal-body').html($('#' + template.content).html());
                if(template.actions) {
                    modal.find('.modal-footer').html(
                        template.actions.reduce(function(str, action) {
                            var title = typeof action.title === "string" ? action.title : action.title[options.context];
                            if(!title)
                                return str;
                            return str + AUFM.Util.template($('#button_template').html(), {
                                id: action.id,
                                title: title,
                                color: action.color ? action.color : AUFM.Constants.DEFAULT_COLOR,
                                font_color: action.font_color ? action.font_color : AUFM.Constants.DEFAULT_FONT_COLOR,
                            });
                        }, "")
                    );
                    modal.find('.modal-footer .btn').click(function(e) {
                        var id = $(this).attr("id");
                        var action = template.actions.find(function(a) { return a.id == id; });
                        var callback = options.actions ? options.actions[id] : undefined;
                        if(action)
                            action.click(modal, callback, e);
                    });
                }
                modal.modal('open');
            },
            templates: {
                building_modal: {
                    id: "building_modal",
                    title: {"create": "Add New Building", "edit": "Edit Building"},
                    content: 'building_modal_template',
                    actions: [
                        {
                            id: "save_building",
                            title: {"create": "Add Building", "edit": "Save Building"},
                            click: function(modal, callback) {
                                var nameValue = modal.find("#building_name").val().trim();
                                if(nameValue.length == 0)
                                    return;
                                AUFM.Util.api({
                                    url: "building" + (modal.context == "edit" ? "/" + modal.item.id() : ""),
                                    type: modal.context == "create" ? "POST" : "PUT",
                                    data: { "name": nameValue },
                                    callback: function(data) {
                                        var building = new AUFM.Schema.Building(data);
                                        if(modal.context == "create")
                                            AUFM.UI.Buildings.add(building);
                                        else {
                                            AUFM.UI.Buildings.replace(building);
                                        }
                                        if(callback)
                                            callback();
                                        modal.modal("close");
                                    },
                                });
                            },
                        },
                        {
                            id: "delete_building",
                            title: {"edit": "Delete Building"},
                            click: function(modal) {
                                AUFM.Util.api({
                                    url: "building/" + modal.item.id(),
                                    type: "DELETE",
                                    callback: function(data) {
                                        AUFM.UI.Buildings.delete(model.item.id());
                                        modal.modal("close");
                                    },
                                });
                            },
                        },
                    ]
                },
                part_modal: {
                    id: "part_modal",
                    title: {"create": "Add New Part", "edit": "Edit Part"},
                    content: 'part_modal_template',
                    actions: [
                        {
                            id: "save_part",
                            title: {"create": "Add New Part", "edit": "Edit Part"},
                            click: function(modal, callback) {
                                var elementID = modal.find("#part_element_id").val().trim();
                                if(elementID.length == 0)
                                    return; // todo: alert min characters.
                                if(!$.isNumeric(elementID))
                                    return; // todo: alert numeric restriction.
                                if(AUFM.UI.Parts.building == undefined)
                                    return; //todo: alert building unset.
                                AUFM.Util.api({
                                    url: "part",
                                    type: modal.context == "create" ? "POST" : "PUT",
                                    data: { 
                                        "building_id": AUFM.UI.Parts.building.id(),
                                        "element_id": elementID
                                     },
                                    callback: function(data) {
                                        AUFM.UI.Parts.add(new AUFM.Schema.Part(data));
                                        if(callback)
                                            callback();
                                        modal.modal("close");
                                    },
                                });
                            }, 
                        },
                        {
                            id: "delete_part",
                            title: {"edit": "Delete Part"},
                            click: function(modal) {
                                AUFM.Util.api({
                                    url: "part/" + modal.item.elementID(),
                                    type: "DELETE",
                                    callback: function(data) {
                                        AUFM.UI.Parts.delete(model.item.id());
                                        modal.modal("close");
                                    },
                                });
                            },
                        },
                    ]
                },
                protocol_modal: {
                    id: "protocol_modal",
                    title: {"create": "Add New Protocol", "edit": "Edit Protocol"},
                    content: 'protocol_modal_template',
                    actions: [
                        {
                            id: "save_protocol",
                            title: {"create": "Add New Part", "edit": "Edit Part"},
                            click: function(modal, callback) {
                                var protocolValue = modal.find("#protocol_value").val().trim();
                                if(protocolValue.length == 0)
                                    return; // todo: alert min characters.
                                if(AUFM.UI.Protocols.part == undefined)
                                    return; //todo: alert part unset.
                                AUFM.Util.api({
                                    url: "protocol",
                                    type: "POST",
                                    data: { 
                                        "value": protocolValue,
                                     },
                                    callback: function(protocolData) {
                                        var protocol = new AUFM.Schema.Protocol(protocolData);
                                        AUFM.Util.api({
                                            url: "part/" + AUFM.UI.Protocols.part.elementID() + "/protocol/" + protocol.id(),
                                            type: "POST",
                                            data: { 
                                                "value": protocolValue,
                                             },
                                            callback: function(data) {
                                                AUFM.UI.Protocols.add(protocol);
                                                if(callback)
                                                    callback();
                                                modal.modal("close");
                                            },
                                        });
                                    },
                                });
                            },
                        },
                        {
                            id: "delete_protocol",
                            title: {"edit": "Delete Protocol"},
                            click: function(modal) {
                                AUFM.Util.api({
                                    url: "part/" + AUFM.UI.Protocols.part.elementID() + "/protocol/" + modal.item.id(),
                                    type: "DELETE",
                                    callback: function(data) {
                                        AUFM.UI.Protocols.delete(model.item.id());
                                        modal.modal("close");
                                    },
                                });
                            },
                        },
                    ]
                },
            },
        },
        Users: {
            users: [],
            card: undefined,
        },
        Buildings: {
            buildings: [],
            card_options: {
                id: "building_card",
                title: "Building",
                search: true,
                collection: function(building) {
                    AUFM.UI.Buildings.close();
                    AUFM.UI.Parts.open(building);
                },
                actions: {
                    title: "Add Building",
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "building_modal",
                        });
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
                            self.buildings.push(new AUFM.Schema.Building(b));
                        });
                        self.card.populate(self.buildings);
                        self.card.fadeIn();
                    },
                });
            },
            close: function() {
                this.card.hide();
            },
            //todo next cycle: abstract the following
            add: function(building) {
                this.buildings.push(building);
                this.card.populate(this.buildings);
            },
            remove: function(id) {
                this.buildings = this.buildings.filter(function(b) { return b.id() != id;});
                this.card.populate(this.buildings);
            },
            replace: function(building) {
                var index = this.buildings.indexOf(function(b) { return b.id() != building.id();});
                if(index >= 0) {
                    this.buildings[index] = building;
                    this.card.populate(this.buildings);
                }
            },
        },
        Parts: {
            building: undefined,
            parts: [],
            card_options: {
                id: "parts_card",
                title: "Parts",
                search: true,
                collection: function(part) {
                    AUFM.UI.Parts.close();
                    AUFM.UI.Protocols.open(part);
                },
                actions: {
                    title: "Add New Part",
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "part_modal",
                        });
                    },
                },
            },
            card: undefined,
            open: function(building) {
                this.building = building ? building : this.building;
                var self = this;
                AUFM.Util.api({
                    url: "building/" + self.building.id() + "/part",
                    callback: function(data) {
                        data.parts.forEach(function(p) {
                            self.parts.push(new AUFM.Schema.Part(p));
                        });
                        self.card.populate(self.parts);
                        self.card.fadeIn();
                    },
                });
            },
            close: function() {
                this.card.hide();
            },
            //todo next cycle: abstract the following
            add: function(part) {
                this.parts.push(part);
                this.card.populate(this.parts);
            },
            remove: function(id) {
                this.parts = this.parts.filter(function(p) { return p.id() != id;});
                this.card.populate(this.parts);
            },
            replace: function(part) {
                var index = this.parts.indexOf(function(p) { return p.id() != part.id();});
                if(index >= 0) {
                    this.parts[index] = part;
                    this.card.populate(this.parts);
                }
            },
        },
        Protocols: {
<<<<<<< HEAD
            part: undefined,
            protocols: [],
            card_options: {
                id: "protcols_card",
                title: "Protocols",
                search: true,
                collapsible: {
                    actions: [
                        {
                            title: "Replace Protocol",
                            click: function(protocol) {},
                        },
                        {
                            title: "Delete Protocol",
                            color: "red",
                            click: function(protocol) {},
                        }
                    ],
                },
                actions: {
                    title: "Attach Protocol",
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "protocol_modal",
                        });
=======
            _part: undefined,
            _protocols: [],
            card_options: {
                id: "protocols_card",
                title: "Protocol",
                collection: function(protocol) {
                    //edit Protocol
                },
                actions: {
                    title: "Add New Protocol",
                    click: function(e) {
                        // trigger add building modal
>>>>>>> dfd2843a41426426fb67d683fe848d82124edc00
                    },
                },
            },
            card: undefined,
            open: function(part) {
<<<<<<< HEAD
                this.part = part;
                var self = this;
                AUFM.Util.api({
                    url: "part/" + self.part.elementID() + "/protocol",
                    callback: function(data) {
                        data.protocols.forEach(function(p) {
                            self.protocols.push(new AUFM.Schema.Protocol(p));
                        });
                        self.card.populate(self.protocols);
                        self.card.fadeIn();
                    },
                });
            },
            close: function() {
                this.card.hide();
            },
            back: function() {
                this.close();
                this.part = undefined;
                this.protocols = [];
                AUFM.UI.Parts.open();
            },
            //todo next cycle: abstract the following
            add: function(protocol) {
                this.protocols.push(protocol);
                this.card.populate(this.protocols);
            },
            remove: function(id) {
                this.protocols = this.protocols.filter(function(p) { return p.id() != id;});
                this.card.populate(this.protocols);
            },
            replace: function(protocol) {
                var index = this.protocols.indexOf(function(p) { return p.id() != protocol.id();});
                if(index >= 0) {
                    this.protocols[index] = protocol;
                    this.card.populate(this.protocols);
                }
=======
                this._part = part
                var self = this;
                AUFM.Util.api({
                    url: "part/" + self._part.pid() + "/protocol",
                    callback: function(data) {
                        data.protocols.forEach(function(p) {
                            self._protocols.push(new AUFM.Schema.Protocol(p));
                        });
                        self.card.populate(self._protocols);
                        self.card.fadeIn();
                    }
                })
            },
            close: function() {
                this.card.fadeOut();
>>>>>>> dfd2843a41426426fb67d683fe848d82124edc00
            },
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

<<<<<<< HEAD
            this.elementID = function() {
                return this._element_id;
            };
=======
            this.pid = function() {
                return this._element_id;
            }
>>>>>>> dfd2843a41426426fb67d683fe848d82124edc00

            this.collection = function() {
                return {
                    id: this._part_id,
                    name: this._element_id,
                };
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
<<<<<<< HEAD
                    content: this.value,
                    button_title: "Replace Protocol"
                }
=======
                    name: this._value,
                };
>>>>>>> dfd2843a41426426fb67d683fe848d82124edc00
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
                data: params.data ? JSON.stringify(params.data) : "",
                contentType: "application/json; charset=utf-8",
                dataType: "json",
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