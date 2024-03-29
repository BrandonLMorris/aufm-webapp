/**
 * Utility functions for the AUFM frontend.
 */
AUFM.Util = {
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
};