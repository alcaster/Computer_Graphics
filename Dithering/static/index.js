parameter_operations = ['ordered_dithering'];


$(document).ready(function () {
    $(".modes > button")
        .click(function () {
            var mode = $(this).attr('id');
            var org_img_base64 = $("#org_img").attr('src');
            var data = {
                'img': org_img_base64.split(',')[1],
                'mode': mode
            };
            if (parameter_operations.includes($(this).attr('id'))) {
                switch ($(this).attr('id')) {
                    case "ordered_dithering":
                        var params_dialog = createDialog("Please input parameters", "", {
                            buttons: {
                                "Go": function () {
                                    var n = params_dialog.find("#n");
                                    var k = params_dialog.find("#k");
                                    data['n'] = parseFloat(n.val());
                                    data['k'] = parseFloat(k.val());
                                    sendToProcesPhoto(data, org_img_base64);
                                    $(this).dialog("close");
                                },
                                "Cancel": function () {
                                    $(this).dialog("close");
                                }
                            }
                        });
                        var new_form =
                            '<label for=\"n\">N</label>' +
                            '<input type=\"number\" step=\"0.01\" id=\"n\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">' +
                            '<label for=\"k\">K</label>' +
                            '<input type=\"number\" step=\"0.01\" id=\"k\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">';
                        params_dialog.find("fieldset").append(new_form);
                        break;
                }
            }
            else {
                sendToProcesPhoto(data, org_img_base64);
            }
        })
        .hide();
});

function changeOrgPhoto() {
    var preview = $('<img width="100%" id="org_img">');
    var file = document.querySelector('input[type=file]').files[0];
    var reader = new FileReader();

    reader.onloadend = function () {
        preview.attr('src', reader.result);
        $(".modes > button").show()
    };

    if (file) {
        reader.readAsDataURL(file);
    } else {
        preview.attr('src', "");
    }
    $("#org").empty();
    $("#gen").empty();
    preview.appendTo("#org")
}

function sendToProcesPhoto(data, org_img_base64) {
    $.ajax("api/process_photo", {
        data: JSON.stringify(data),
        contentType: 'application/json',
        type: 'POST',
        success: function (data) {
            var preview = $('<img width="100%" id="gen_img">');
            preview.attr('src', org_img_base64.split(',')[0] + ',' + data["img"]);
            $("#gen").empty();
            preview.appendTo("#gen")
        }
    })
}

function createDialog(title, text, options) {
    return $("<div class='dialog-confirm' title='" + title + "'><p>" + text + "</p><form><fieldset></fieldset></form></div>").dialog(
        Object.assign({}, {
            resizable: false,
            height: "auto",
            width: 400,
            modal: true,
            closeText: ""
        }, options)
    );
}