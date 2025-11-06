/// <reference path="../../scripts/jquery-3.6.0.min.js" />


function GenerateGoogleCapchaToken(enableGoogleRecapcha, googleCapchaClientToken, captchaToken) {
    //console.log(enableGoogleRecapcha);
    //console.log(googleCapchaClientToken);
    //console.log(captchaToken); 
    var elableGoogleRecapcha = enableGoogleRecapcha.val();
    //console.log('capcha status is - ' + elableGoogleRecapcha);
    if (elableGoogleRecapcha.toLowerCase() == 'true') {
        var ClientCapcha = decodeURIComponent(googleCapchaClientToken.val());
        //console.log(ClientCapcha);
        var url = 'https://www.google.com/recaptcha/api.js?render=' + ClientCapcha;


        //return $.when($.getScript(url, function (data, textStatus, jqxhr) {
        //    return grecaptcha.ready(function () {
        //         //var ClientCapcha = $("#<%=googleCapchaClientToken.ClientID%>").val();
        //        return grecaptcha.execute(ClientCapcha, { action: 'Validation' })
        //             .then(function (token) {
        //                 captchaToken.val(token);
        //                 alert('token generated');
        //             });
        //     });
        // })).then(function (data, textStatus, jqXHR) {
        //     alert("promise call");
        // });

        try {
            $.getScript(url, function (data, textStatus, jqxhr) {
                grecaptcha.ready(function () {
                    //var ClientCapcha = $("#<%=googleCapchaClientToken.ClientID%>").val();
                    try {
                        grecaptcha.execute(ClientCapcha, { action: 'Validation' })
                            .then(function (token) {
                                captchaToken.val(token);
                                //console.log('token generated');
                            });
                    } catch (e) {

                    }
                }
                );
            });
        } catch (e) {

        }

       

    }
}