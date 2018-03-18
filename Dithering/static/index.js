parameter_operations = ['ordered_dithering', 'uniform_color_quantization'];


$(document).ready(function () {
    $(".modes > button")
        .click(function () {
            var mode = $(this).attr('id');
            var org_img_base64 = $("#org_img").attr('src');
            var data = {
                'img': org_img_base64.split(',')[1],
                'mode': mode
            }, params_dialog, new_form;


            if (parameter_operations.includes($(this).attr('id'))) {
                console.log("lol2");

                switch ($(this).attr('id')) {
                    case "ordered_dithering":
                        new_form =
                            '<label for=\"n\">N</label>' +
                            '<input type=\"number\" id=\"n\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">' +
                            '<label for=\"k\">K</label>' +
                            '<input type=\"number\" id=\"k\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">';

                        params_dialog = createParamsDialog(new_form, function () {
                            var n = params_dialog.find("#n");
                            var k = params_dialog.find("#k");
                            data['n'] = parseInt(n.val());
                            data['k'] = parseInt(k.val());
                            sendToProcesPhoto(data, org_img_base64);
                            $(this).dialog("close");
                        });
                        break;
                    case "uniform_color_quantization":
                        console.log("lol3");
                        new_form =
                            '<label for=\"Kr\">Kr</label>' +
                            '<input type=\"number\" id=\"Kr\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">' +
                            '<label for=\"Kg\">Kg</label>' +
                            '<input type=\"number\" id=\"Kg\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">' +
                            '<label for=\"Kb\">Kb</label>' +
                            '<input type=\"number\" id=\"Kb\" value=\"2\" class=\"text ui-widget-content ui-corner-all\">';
                        console.log("lol4");

                        params_dialog = createParamsDialog(new_form, function () {
                            var kr = params_dialog.find("#Kr");
                            var kg = params_dialog.find("#Kg");
                            var kb = params_dialog.find("#Kb");
                            data['kr'] = parseInt(kr.val());
                            data['kg'] = parseInt(kg.val());
                            data['kb'] = parseInt(kb.val());
                            sendToProcesPhoto(data, org_img_base64);
                            $(this).dialog("close");
                        });

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

function createParamsDialog(fields, callback) {
    return createDialog("Please input parameters", "", "<form><fieldset>" + fields + "</fieldset></form>", {
        resizable: false,
        height: "auto",
        width: 400,
        modal: true,
        closeText: "",
        buttons: {
            "Go": callback,
            "Cancel": function () {
                $(this).dialog("close");
            }
        }
    })
}

function createDialog(title, text, extra, options) {
    return $("<div class='dialog-confirm' title='" + title + "'><p>" + text + "</p>" + extra + "</div>").dialog(options);
}