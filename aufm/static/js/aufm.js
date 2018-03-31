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
            $("#protocol_families").click(AUFM.UI.ProtocolFamilies.open);

            AUFM.UI.Cards.initialize();
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
                collection_action: undefined,
                collapsible: '<ul class="collapsible" data-collapsible="accordion">/<ul>',
                collapsible_item: undefined,
                property_container: undefined,
                property_row: undefined,
            },
            initialize: function() {
                // set templates.
                this.templates.card = $('#card_template').html();
                this.templates.collection_item = $('#collection_item_template').html();
                this.templates.collapsible_item = $('#collapsible_item_template').html();
                this.templates.collection_action = $('#collection_action_template').html();
                this.templates.property_container = $('#property_container_template').html();
                this.templates.property_row = $('#property_row_template').html();
            },
            create: function(options) {
                var self = this;
                var card = $(this.templates.card);
                if(options.id == undefined)
                    throw "Missing required parameter 'id' for card.";
                else 
                    card.attr("id", options.id);

                // Card title.
                var title = options.title ? typeof options.title == "string" ? options.title : options.title() : "";
                if(options.title)
                    card.find('.card-title').html(title);
                
                // Setting up searching through content.
                if(options.search) {
                    card.find('.search-input input').attr("id", options.id + "_search").on('input', function(e) {
                        var value = $(this).val().toLowerCase().trim();
                        if(value == "")
                            card.find('.searchable').show();
                        else
                            card.find('.searchable .search-value').each(function(index) {
                                var ele = $(this);
                                if(!ele.html().toLowerCase().includes(value))
                                    ele.parent().hide();
                                else
                                    ele.parent().show();
                            });
                    });
                    card.find('.search-input label').attr("for", options.id + "_search").html("Search " + title + "...");
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
                        if(options.collection.actions) {
                            content.find('.collection-item').each(function() {
                                var container = $(this).find('.actions');
                                for(action in options.collection.actions) {
                                    container.append(AUFM.Util.template(self.templates.collection_action, {
                                        action: action,
                                        icon: options.collection.actions[action].icon,
                                    }));
                                }
                            });
                            content.find('.collection-item .action').click(function(e) {
                                var action = $(this).data("action");
                                var collectionID = $(this).parents('.collection-item').first().data("id");
                                var item = collection.find((c) => { return c.id() == collectionID; });
                                options.collection.actions[action].click(item);
                                e.preventDefault();
                                e.stopPropagation();
                            });
                        }
                        content.find('.collection-item').click(function(e) {
                            var id = $(this).data("id");
                            var item = collection.find((c) => { return c.id() == id; });
                            options.collection.click(item);
                            e.stopPropagation();
                            e.preventDefault();
                        });
                    };
                } else if(options.collapsible) { // todo: refactor & make understandable
                    content.html(this.templates.collapsible);
                    card.populate = function(collection) {
                        card.collection = collection;
                        content.find('.collapsible').html(
                            card.collection.reduce(function(str, item) {
                                if(!item.collection)
                                    return str;
                                var collection = item.collection();
                                return str + AUFM.Util.template(self.templates.collapsible_item, {
                                    id: collection.id,
                                    value: collection.value,
                                    actions: options.collapsible.actions.reduce(function(str, action) {
                                        return str + AUFM.Util.template($('#button_template').html(), {
                                            id: action.id,
                                            title: action.title,
                                            color: action.color ? action.color : AUFM.Constants.DEFAULT_COLOR,
                                            font_color: action.font_color ? action.font_color : AUFM.Constants.DEFAULT_FONT_COLOR,
                                        }); // todo: abstract
                                    }, "")
                                });
                            }, "")
                        );
                        content.find('.collapsible').collapsible();
                        // Load the sublist upon clicking
                        // FIXME This is kinda jank; didn't see a better way
                        if (options.sublist) {
                            sublist = options.sublist;
                            content.find('.collapsible-header').click(function() {
                                var itemId = $(this).parent().data("id");
                                AUFM.Util.api({
                                    url: sublist.endpoint + itemId,
                                    callback: function(data) {
                                        subitems = data[sublist.key].map(function(e) {return sublist.schema(e);});
                                        content.find('#collapsible-sublist').html(
                                            '<ul class="collection">' +
                                            subitems.reduce(function(str, item) {
                                                // FIXME I'M DYING
                                                i = item.collection();
                                                return str + '<li class="collection-item" data-id="' + i.id + '">' + i.value + '<div class="actions"></div></li>';
                                            }, "") +
                                            '</ul><br>'
                                        );
                                        if (options.sublist.actions) {
                                            content.find('.collection-item').each(function() {
                                                // Need to template out collection_action_template
                                                var container = $(this).find('.actions');
                                                for(action in sublist.actions) {
                                                    container.append(AUFM.Util.template(self.templates.collection_action, {
                                                        action: action,
                                                        icon: sublist.actions[action].icon,
                                                    }));
                                                }
                                            });
                                            content.find('.collection-item .action').click(function(e) {
                                                var action = $(this).data("action");
                                                var collectionID = $(this).parents('.collection-item').first().data("id");
                                                var superID = $(this).parents('.active').first().data('id');
                                                var subItem = subitems.find((c) => { return c.id() == collectionID; });
                                                var superItem = card.collection.find((c) => {return c.id() == superID;});
                                                sublist.actions[action].click(superItem, subItem);
                                                e.preventDefault();
                                                e.stopPropagation();
                                            });
                                        }
                                    }
                                });
                            });
                        }
                        content.find('.collapsible-body .btn').click(function() {
                            var action = $(this).data("id");
                            var collectionID = $(this).parents("li").first().data("id");
                            var collection = card.collection.find(function(c){ return c.collection().id == collectionID; });
                            if(!collection)
                                return;
                            options.collapsible.actions.forEach(function(a) {
                                if(a.id == action)
                                    a.click(collection);
                            });
                        });
                    };
                } else if(options.content)
                    content.html(options.content);
                else
                    throw "Invalid card content.";

                if(options.actions) {
                    var added = card.find('.card-action').html(options.actions.reduce(function(str, item) {
                        return str + AUFM.Util.template($('#button_template').html(), {
                            title: item.title,
                            id: item.id,
                            color: item.color ? item.color : AUFM.Constants.DEFAULT_COLOR,
                            font_color: item.font_color ? item.font_color : AUFM.Constants.DEFAULT_FONT_COLOR,
                        });
                    }, ""));
                    added.find('a').click(function() {
                        action = $(this).data("id");
                        options.actions.forEach(function(a) {
                            if (a.id == action) a.click();
                        });
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
                if(template.width)
                    modal.css("width", template.width + "%");
                modal.item = options.item;
                modal.action = options.action;
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
                        var id = $(this).attr("data-id");
                        var action = template.actions.find(function(a) { return a.id == id; });
                        var callback = options.actions ? options.actions[id] : undefined;
                        if(action)
                            action.click(modal, callback, e);
                    });
                }
                if(template.create)
                    template.create(modal, options.item);
                // Setting up searching through content.
                if(template.search) {
                    modal.find('.search-input input').attr("id", options.id + "_search").on('input', function(e) {
                        var value = $(this).val().toLowerCase().trim();
                        if(value === "")
                            modal.find('.searchable').show();
                        else
                            modal.find('.searchable .search-value').each(function(index) {
                                var ele = $(this);
                                if(!ele.html().toLowerCase().includes(value))
                                    ele.parent().hide();
                                else
                                    ele.parent().show();
                            });
                    });
                    modal.find('.search-input label').attr("for", options.id + "_search").html("Search...");
                }
                Materialize.updateTextFields();
                modal.modal('open');
            },
            templates: {
                building_modal: {
                    id: "building_modal",
                    title: {"create": "Add New Building", "edit": "Edit Building"},
                    content: 'building_modal_template',
                    width: 35,
                    create: function(modal, item) {
                        if(item)
                            modal.find('#building_name').val(item.collection().value).focus();
                    },
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
                            color: "red",
                            click: function(modal) {
                                modal.item.remove(function() {
                                    AUFM.UI.Buildings.remove(modal.item.id());
                                    modal.modal("close");
                                });
                            },
                        },
                    ]
                },
                part_modal: {
                    id: "part_modal",
                    title: {"create": "Add New Part", "edit": "Edit Part"},
                    content: 'part_modal_template',
                    width: 35,
                    create: function(modal, item) {
                        if(typeof item !== "undefined") {
                            modal.find('#part_name').val(item.name()).focus();
                            modal.find('#part_element_id').val(item.elementID());
                        }
                    },
                    actions: [
                        {
                            id: "save_part",
                            title: {"create": "Add New Part", "edit": "Edit Part"},
                            click: function(modal, callback) {
                                var elementID = modal.find("#part_element_id").val().trim();
                                var partName = modal.find("#part_name").val().trim();
                                if(elementID.length == 0)
                                    return; // todo: alert min characters.
                                if(!$.isNumeric(elementID))
                                    return; // todo: alert numeric restriction.
                                if(AUFM.UI.Parts.building == undefined)
                                    return; //todo: alert building unset.
                                AUFM.Util.api({
                                    url: "part" + (modal.context == "edit" ? "/" + modal.item.elementID() : ""),
                                    type: modal.context == "create" ? "POST" : "PUT",
                                    data: { 
                                        "building_id": AUFM.UI.Parts.building.id(),
                                        "element_id": elementID,
                                        "part_name": partName
                                     },
                                    callback: function(data) {
                                        var part = new AUFM.Schema.Part(data);
                                        if(modal.context == "create")
                                            AUFM.UI.Parts.add(part);
                                        else {
                                            AUFM.UI.Parts.replace(part);
                                        }
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
                            color: "red",
                            click: function(modal) {
                                modal.item.remove(function() {
                                    AUFM.UI.Parts.remove(modal.item.id());
                                    modal.modal("close");
                                });
                            },
                        },
                    ]
                },
                protocol_modal: {
                    id: "protocol_modal",
                    title: {"create": "Add New Protocol", "edit": "Edit Protocol"},
                    content: 'protocol_modal_template',
                    width: 35,
                    create: function(modal, item) {
                        if(typeof item !== "undefined") {
                            modal.find('#protocol_value').val(item.collection().value).focus();
                        }
                    },
                    actions: [
                        {
                            id: "save_protocol",
                            title: {"create": "Add New Protocol", "edit": "Save Changes"},
                            color: "green",
                            click: function(modal, callback) {
                                var protocolValue = modal.find("#protocol_value").val().trim();
                                if(protocolValue.length == 0)
                                    return; // todo: alert min characters.
                                if(AUFM.UI.Protocols.part == undefined)
                                    return; //todo: alert part unset.
                                // Create the new protocol
                                AUFM.Util.api({
                                    url: "protocol" + (modal.context == "edit" ? "/" + modal.item.id() : ""),
                                    type: modal.context == "create" ? "POST" : "PUT",
                                    data: { 
                                        "value": protocolValue,
                                     },
                                    callback: function(protocolData) {
                                        var protocol = new AUFM.Schema.Protocol(protocolData);
                                        if(modal.context == "edit") {
                                            AUFM.UI.Protocols.replace(protocol);
                                            if(callback)
                                                callback();
                                            modal.modal("close");
                                            return;
                                        }
                                        // Now associate the protocol with the part
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
                            id: "cancel_changes",
                            title: {"edit": "Cancel"},
                            click: function(modal) {
                                modal.modal("close");
                            }
                        },
                    ]
                },
                protocol_family_modal: {
                    id: "protocol_family_modal",
                    title: {
                        "create": "Add New Protocol Family",
                        "edit": "Edit Protocol Family",
                    },
                    content: "protocol_family_modal_template",
                    width: 35,
                    create: function(modal, item) {
                        if (item) {
                            modal.find('#protocol_familly_value').val(item.collection().value).focus();
                        }
                    },
                    actions: [
                        {
                            id: "save_protocol_family",
                            title: {"create": "Save New Protocol Family", "edit": "Save Changes"},
                            color: "green",
                            click: function(modal, callback) {
                                var familyValue = modal.find("#protocol_family_value").val().trim();
                                if(familyValue.length === 0) return;
                                AUFM.Util.api({
                                    url: 'protocol-family' + (modal.context == "edit" ? "/" + modal.item.id() : ""),
                                    type: modal.context == "create" ? 'POST' : "PUT",
                                    data: {'family_name': familyValue},
                                    callback: function(data) {
                                        var fam = new AUFM.Schema.ProtocolFamily(data);
                                        if (modal.context == "create") {
                                            AUFM.UI.ProtocolFamilies.add(fam);
                                        } else {
                                            AUFM.UI.ProtocolFamilies.replace(fam);
                                        }
                                        modal.modal("close");
                                    }
                                });
                            }
                        },
                        {
                            id: "cancel_changes",
                            title: {"edit": "Cancel"},
                            click: function(modal) {modal.modal("close");}
                        },
                    ],
                },
                protocol_list_modal: {
                    id: "protocol_list_modal",
                    title: {
                        "add_existing": "Add Existing Protocol",
                        "add_to_family": "Add Protocol to Family"
                    },
                    search: true,
                    content: 'protocol_list_modal_template',
                    width: 70,
                    create: function(modal, item) {
                        protocols = [];
                        AUFM.Util.api({
                            url: "protocol",
                            callback: function(data) {
                                data.forEach(function(b) {
                                    protocols.push(new AUFM.Schema.Protocol(b));
                                });
                                modal.find('#protocol_list').html(AUFM.UI.Cards.templates.collection);
                                modal.find('.collection').html(
                                    protocols.reduce(function(str, item) {
                                        if(!item.collection) return str;
                                        return str + AUFM.Util.template(AUFM.UI.Cards.templates.collection_item, item.collection());
                                    }, "")
                                );
                                modal.find('.collection-item').click(function(e) {
                                    var id = $(this).data("id");
                                    var item = protocols.find((c) => { return c.id() == id; });
                                    modal.action(item);
                                    e.stopPropagation();
                                    e.preventDefault();
                                });
                            },
                        });
                    },
                    actions: [
                    
                    ]
                },
                protocol_family_list_modal: {
                    id: "protocol_family_list_modal",
                    title: {
                        "add_from_family": "Add Protocols from Family",
                    },
                    search: true,
                    content: 'protocol_family_list_modal_template',
                    width: 70,
                    create: function(modal, item) {
                        families = [];
                        AUFM.Util.api({
                            url: "protocol-family",
                            callback: function(data) {
                                data.forEach(function(b) {
                                    families.push(new AUFM.Schema.ProtocolFamily(b));
                                });
                                modal.find('#family_list').html(AUFM.UI.Cards.templates.collection);
                                modal.find('.collection').html(
                                    families.reduce(function(str, item) {
                                        if(!item.collection) return str;
                                        return str + AUFM.Util.template(AUFM.UI.Cards.templates.collection_item, item.collection());
                                    }, "")
                                );
                                // Add the action for clicking on each collection item
                                modal.find('.collection-item').click(function(e) {
                                    var id = $(this).data("id");
                                    var item = families.find((c) => { return c.id() == id; });
                                    modal.action(item);
                                    e.stopPropagation();
                                    e.preventDefault();
                                });
                            },
                        });
                    }
                }
            },
        },
        Breadcrumb: {
            breadcrumb_stack: [],
            push: function(card) {
                if(this.breadcrumb_stack.includes(card))
                    return;
                $('#card_breadcrumb .breadcrumb').off().click(this.click);
                $('#card_breadcrumb').append(AUFM.Util.template($('#breadcrumb_template').html(), {
                    card: card,
                    title: card,
                }));
                this.breadcrumb_stack.push(card);
            },
            clear: function() {
                $('#card_breadcrumb *').remove();
            },
            click: function(e) {
                var card = $(this).attr("data-card");
                var breadcrumb = $(this);
                AUFM.UI.Breadcrumb.breadcrumb_stack.splice(breadcrumb.index() + 1);
                breadcrumb.nextAll('.breadcrumb').remove();
                if(AUFM.UI[card])
                    AUFM.UI[card].open();
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
                collection: {
                    click: function(building) {
                        AUFM.UI.Buildings.close();
                        AUFM.UI.Parts.open(building);
                    },
                    actions: {
                        edit: {
                            icon: "edit",
                            click: function(building) {
                                AUFM.UI.Modals.open({
                                    template: "building_modal",
                                    context: "edit",
                                    item: building,
                                });
                            },
                        },
                        remove: {
                            icon: "delete",
                            click: function(building) {
                                building.remove(function() {
                                    AUFM.UI.Buildings.remove(building.id());
                                });
                            },
                        },
                    },
                },
                actions: [{
                    title: "Add Building",
                    id: "add_building",
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "building_modal",
                        });
                    },
                }],
            },
            card: undefined,
            open: function() {
                var self = this;
                $('.content-area').hide();
                self.card = self.card ? self.card : AUFM.UI.Cards.create(this.card_options);
                self.buildings = [];
                AUFM.Util.api({
                    url: "building",
                    callback: function(data) {
                        data.forEach(function(b) {
                            self.buildings.push(new AUFM.Schema.Building(b));
                        });
                        self.card.populate(self.buildings);
                        self.card.fadeIn();
                        AUFM.UI.Breadcrumb.push("Buildings");
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
                var index = this.buildings.findIndex(function(b) { return b.id() == building.id();});
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
                title: function() {
                    return "Parts for " + AUFM.UI.Parts.building.collection().value;
                },
                search: true,
                collection: {
                    click:function(part) {
                        AUFM.UI.Parts.close();
                        AUFM.UI.Protocols.open(part);
                    },
                    actions: {
                        edit: {
                            icon: "edit",
                            click: function(part) {
                                AUFM.UI.Modals.open({
                                    template: "part_modal",
                                    context: "edit",
                                    item: part,
                                });
                            },
                        },
                        remove: {
                            icon: "delete",
                            click: function(part) {
                                part.remove(function() {
                                    AUFM.UI.Parts.remove(part.id());
                                });
                            },
                        },
                    },
                },
                actions: [{
                    title: "Add New Part",
                    id: "new_part",
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "part_modal",
                        });
                    },
                }],
            },
            card: undefined,
            open: function(building) {
                this.building = building ? building : this.building;
                var self = this;
                $('.content-area').hide();
                self.card = AUFM.UI.Cards.create(this.card_options);
                self.parts = [];
                AUFM.Util.api({
                    url: "building/" + self.building.id() + "/part",
                    callback: function(data) {
                        data.parts.forEach(function(p) {
                            self.parts.push(new AUFM.Schema.Part(p));
                        });
                        self.card.populate(self.parts);
                        self.card.fadeIn();
                        AUFM.UI.Breadcrumb.push("Parts");
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
                var index = this.parts.findIndex(function(p) { return p.id() == part.id();});
                if(index >= 0) {
                    this.parts[index] = part;
                    this.card.populate(this.parts);
                }
            },
        },
        Protocols: {
            part: undefined,
            protocols: [],
            card_options: {
                id: "protcols_card",
                title: function() {
                    return "Protocols for " + AUFM.UI.Protocols.part.collection().value;
                },
                search: true,
                collapsible: {
                    actions: [
                        {
                            title: "Edit Protocol",
                            id: "replace_protocol",
                            click: function(protocol) {
                                AUFM.UI.Modals.open({
                                    template: "protocol_modal",
                                    context: "edit",
                                    item: protocol,
                                });
                            },
                        },
                        {
                            title: "Delete Protocol",
                            id: "delete_protocol",
                            color: "red",
                            click: function(protocol) {
                                protocol.remove(function() {
                                    AUFM.UI.Protocols.remove(protocol.id());
                                });
                            },
                        }
                    ],
                },
                actions: [{
                        title: "New Protocol",
                        id: "attach_protocol",
                        click: function(e) {
                            AUFM.UI.Modals.open({
                                template: "protocol_modal",
                            });
                        },
                    },
                    {
                        title: "Add Protocols from Family",
                        id: "from_family",
                        click: function(e) {
                            AUFM.UI.Modals.open({
                                // TODO: Reload part list when closing
                                template: "protocol_family_list_modal",
                                context: "add_from_family",
                                action: function(family) {
                                    // Add all the protocols from this family to the part
                                    var eid = AUFM.UI.Protocols.part.elementID();
                                    // Get the protocols associated with the family
                                    AUFM.Util.api({
                                        url: 'protocol-family/' + family.id(),
                                        callback: function(data) {
                                            // Add each protocol to the part
                                            data.protocols.forEach(function(p) {
                                                AUFM.Util.api({
                                                    url: 'part/' + eid + '/protocol/' + p.protocol_id,
                                                    type: 'POST',
                                                    callback: function(data) {}
                                                });
                                            });
                                        }
                                    });
                                }
                            });
                        }
                    },
                    {
                        title: "Add Existing Protocol",
                        id: "add_existing",
                        click: function(e) {
                            AUFM.UI.Modals.open({
                                template: "protocol_list_modal",
                                context: "add_existing",
                                action: function(protocol) {
                                    var eid = AUFM.UI.Protocols.part.elementID();
                                    AUFM.Util.api({
                                        url: 'part/' + eid + '/protocol/' + protocol.id(),
                                        type: 'POST',
                                        callback: function(data) {
                                            // TODO: Reload protocols list
                                        }
                                    });
                                }
                            });
                        }
                    }
                ],
            },
            card: undefined,
            open: function(part) {
                this.part = part;
                var self = this;
                $('.content-area').hide();
                self.card = AUFM.UI.Cards.create(this.card_options);
                self.protocols = [];
                AUFM.Util.api({
                    url: "part/" + self.part.elementID() + "/protocol",
                    callback: function(data) {
                        data.protocols.forEach(function(p) {
                            self.protocols.push(new AUFM.Schema.Protocol(p));
                        });
                        self.card.populate(self.protocols);
                        self.card.fadeIn();
                        AUFM.UI.Breadcrumb.push("Protocols");
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
                var index = this.protocols.findIndex(function(p) { return p.id() == protocol.id();});
                if(index >= 0) {
                    this.protocols[index] = protocol;
                    this.card.populate(this.protocols);
                }
            },
        },
        ProtocolFamilies: {
            families: [],
            card_options: {
                id: "protcols_card",
                title: "Protocol Families",
                search: true,
                sublist: {
                    endpoint: "protocol-family/",
                    key: 'protocols',
                    id: "protocol_id",
                    schema: function(e) {return new AUFM.Schema.Protocol(e);},
                    actions: {
                        remove: {
                            icon: "delete",
                            click: function(family, protocol) {
                                console.log('Trashcan hit');
                                console.log(family);
                                console.log(protocol);
                                family.removeProtocol(protocol, function() {
                                    // FIXME: Should remove the protocol from the sublist
                                });
                            },
                        },
                    },
                },
                collapsible: {
                    actions: [
                        {
                            title: "Edit Protocol Family",
                            id: "edit_family",
                            click: function(family) {
                                // FIXME
                                AUFM.UI.Modals.open({
                                    template: "protocol_family_modal",
                                    context: "edit",
                                    item: family,
                                });
                            },
                        },
                        {
                            title: "Add Protocol to Family",
                            id: "add_to_family",
                            click: function(family) {
                                AUFM.UI.Modals.open({
                                    template: "protocol_list_modal",
                                    context: "add_to_family",
                                    action: function(protocol) {
                                        AUFM.Util.api({
                                            url: 'protocol-family/' + family.id() + '/protocol/' + protocol.id(),
                                            type: 'POST',
                                            // data: {},
                                            callback: function(data) {
                                                // TODO: Reload the sublist when done
                                            }
                                        })
                                    }
                                });
                            },
                        },
                        {
                            title: "Delete Protocol Family",
                            id: "delete_family",
                            color: "red",
                            click: function(family) {
                                family.remove(function() {
                                    AUFM.UI.ProtocolFamilies.remove(family.id());
                                });
                            },
                        }
                    ],
                },
                actions: [{
                    title: "Create New Protocol Family",
                    id: 'new_protocol_family',
                    click: function(e) {
                        AUFM.UI.Modals.open({
                            template: "protocol_family_modal",
                        });
                    },
                }],
            },
            card: undefined,
            open: function() {
                var self = AUFM.UI.ProtocolFamilies;
                $(".content-area").hide();
                self.card = AUFM.UI.Cards.create(self.card_options);
                self.families = [];
                AUFM.Util.api({
                    url: "protocol-family",
                    callback: function(data) {
                        if (data.length > 0) {
                            data.forEach(function(f) {
                                self.families.push(new AUFM.Schema.ProtocolFamily(f));
                            });
                        }
                        self.card.populate(self.families);
                        self.card.fadeIn();
                        AUFM.UI.Breadcrumb.clear();
                        AUFM.UI.Breadcrumb.push("Protocol Families");
                    }
                });
            },
            close: function() {
                this.card.hide();
            },
            back: function() {
                this.close();
                this.part = undefined;
                this.families = [];
            },
            add: function(family) {
                this.families.push(family);
                this.card.populate(this.families);
            },
            remove: function(id) {
                this.families = this.families.filter(function(p) { return p.id() != id;});
                this.card.populate(this.families);
            },
            replace: function(family) {
                var index = this.families.findIndex(function(p) { return p.id() == family.id();});
                if(index >= 0) {
                    this.families[index] = family;
                    this.card.populate(this.families);
                }
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
                    console.log(text + " " + error);
                },
            });
        },
    },
};

$(document).ready(function(e) {
    AUFM.UI.initialize();
});
