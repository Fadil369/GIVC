var CssErrorClassName = "error";
///////////////////Start of Common Validators/////////////////////////////////////////

function ValidateReCaptcha(lbl) {
    var response = grecaptcha.getResponse();
    if (response.length == 0) {
        lbl.show();
        return false;
    }
    else {
        lbl.hide();
        return true;
    }
}

function ValidateEmpty(txt) {
    if (txt.val().trim().length == 0) {
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        txt.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateEmptytxt(lbl, txt) {
    if (txt.val().trim().length == 0) {

        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateEmptytxtwithError(lbl1, lbl2, lbl3, txt) {
    if (txt.val().trim().length == 0) {
        lbl3.hide();
        lbl1.addClass(CssErrorClassName);
        lbl2.show();
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl1.removeClass(CssErrorClassName);
        lbl2.hide();

        txt.removeClass(CssErrorClassName);
        return true;
    }
}



function ValidateEmptytxtwithoutlabel(txt) {
    if (txt.val().trim().length == 0) {
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        txt.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateTextArea(lbl, txt) {
    if (txt.val().trim().length == 0 || txt.val().trim().length > 250) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}
//tabish added for contactus
function ValidateTextArea(lbl, txt, maxlength) {
    if (txt.val().trim().length == 0 || txt.val().trim().length > maxlength) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

//Created to add error class on the parent span of the textbox
function ValidateTextBoxMaxLength(txt, maxlength) {
    if (txt.val().trim().length == 0 || txt.val().trim().length > maxlength) {
        txt.parent().addClass(CssErrorClassName);
        return false;
    }
    else {
        txt.parent().removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateLength(lbl, txt, minLength) {
    if (txt.val().trim().length > minLength) {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
    else {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }

}

function ValidateURL(lbl, txt) {
    // var regexp =/^(([a-zA-Z][0-9a-zA-Z+/\/\-/\/\.]*:)?/{0,2}[0-9a-zA-Z;/?:@&=+$/\/\./\/\-_!~*'()%]+)?(#[0-9a-zA-Z;/?:@&=+$/\/\./\/\-_!~*'()%]+)?$/;
    var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
    var regex = new RegExp(regexp);
    if (!txt.val().trim().match(regex)) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}
function ValidateLengh(lbl, txt, minLength, maxLength) {
    if (txt.val().trim().length > 0) {

        if (txt.val().trim().length >= minLength
            && txt.val().trim().length <= maxLength) {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
                txt.removeClass(CssErrorClassName);
            }
            return true;
        }
        else {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
                txt.addClass(CssErrorClassName);
            }
            return false;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
            txt.addClass(CssErrorClassName);
        }
        return false;
    }

}
function ValidateLenghTxt(txt, minLength, maxLength) {
    if (txt.val().trim().length > 0) {
        if (txt.val().trim().length >= minLength
            && txt.val().trim().length <= maxLength) {

            return true;
        }
        else {

            return false;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }

}

function ValidateChangePasswordLengh(lbl, txt, minLength, maxLength) {
    if (txt.valueOf().length > 0) {
        if (txt.val().trim().length >= minLength
            && txt.val().trim().length >= maxLength) {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
        else {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }

}

function ValidateEmail(lbl, txt) {

    if (txt.valueOf().length > 0) {

        var re = /^([\w-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([\w-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)$/;
        //   var re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]{1,3}+\.[a-zA-Z]{2,4}$/;

        if (!txt.val().trim().match(re)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
                txt.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
                txt.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
            txt.addClass(CssErrorClassName);
        }
        return false;
    }
}

//Saudi Mobile Phone Length
function ValidateSaudiMobilePhoneLength(lbl, txt) {

    if (txt.val().length == 0 || txt.val().length < 10)
        return false;

    if (txt.val().length >= 2 && txt.val().substring(0, 2) == "05")
        return txt.val().length == 10;

    if (txt.val().length >= 4 && txt.val().substring(0, 4) == "+966")
        return txt.val().length == 13;

    return true;
}

//Saudi Mobile Phone
function ValidateSaudiMobilePhone(lbl, txt) {
    var isvalid = true;

    if (txt.valueOf().length == 0)
        isvalid = false;

    //var re = /^(009665|9665|\+9665|05|5)(5|0|3|6|4|9|1|8|7)([0-9]{7})$/;
    var re = /^(05|\+9665)([0-9]{8})$/;
    if (!txt.val().match(re))
        isvalid = false;

    if (!isvalid) {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
    }
    else {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
    }
    return isvalid;
}

//Validate Alpha Numeric Values along with -
function ValidateAlphaNumWithHyphen(lbl, txt) {

    if (txt.valueOf().length > 0) {
        var regexp = /^[a-zA-Z0-9-_]+$/;

        if (!txt.val().trim().match(regexp)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }
}

function ValidatePassword(lbl, txt) {
    if (txt.valueOf().length > 0) {

        //var re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[\)\/><�,\.\*%\]\[�=_ \{\}\$&\-!\+\^\(])[A-Za-z\d\)\/><�,\.\*%\]\[�=_ \{\}\$&\-!\+\^\(]{8,50}$/;          /* /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/; */
        //[{}$&\\-!+^()/><\\',.*%\\]\\[=_]
        var re = /^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[/[{}$&\-!+^()/><\',.*%\]=_])(?=.{8,})/;
        if (!txt.val().trim().match(re)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }
}

function ValidateText(lbl, txt) {
    if (txt.valueOf().length > 0) {

        var re = /^(([a-zA-Z\u0600-\u06FF .-]+)|([?-?0-9 .-]+))$/;

        if (!txt.val().trim().match(re)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }
}


function ValidateEnglishLetterAndNumbers(lbl, txt) {
    if (txt.valueOf().length > 0) {

        var re = /^(([a-zA-Z .-]+)|([?-?0-9 .-]+))$/;

        if (!txt.val().trim().match(re)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }
}

function ValidateDropDown(lbl, ddl) {

    if ($("option:selected", ddl).val().trim() == '' || $("option:selected", ddl).val().trim() == '-1') {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}
function ValidateDropDownDependent(lbl, ddl) {

    if ($("option:selected", ddl).val().trim() == '') {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateDropDownSelectedValue(lbl, ddlValue) {

    if (ddlValue != '' && ddlValue != '0' && ddlValue != "-1") {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
    else {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
}

function ValidateDropDownSelectedValuedderror(ddl) {
  
    if ($("option:selected", ddl).val().trim() == '' || $("option:selected", ddl).val().trim() == '-1') {
        ddl.addClass(CssErrorClassName);
        return false;
    }
    else {
        ddl.removeClass(CssErrorClassName);
        return true;
    }
}

//Created to add error class on the parent span of the drop down!
function ValidateDropDownerror(ddl) {

    if ($("option:selected", ddl).val().trim() == '' || $("option:selected", ddl).val().trim() == '-1') {
        ddl.parent().parent().siblings().addClass(CssErrorClassName);
        ddl.addClass(CssErrorClassName);
        return false;
    }
    else {
        ddl.parent().parent().siblings().removeClass(CssErrorClassName);
        ddl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateDropDownerrorFraud(ddl) {

    if ($("option:selected", ddl).val().trim() == '' || $("option:selected", ddl).val().trim() == '-1') {
        // ddl.parent().parent().siblings().addClass(CssErrorClassName);
        ddl.addClass(CssErrorClassName);
        return false;
    }
    else {
        //ddl.parent().parent().siblings().removeClass(CssErrorClassName);
        ddl.removeClass(CssErrorClassName);
        return true;
    }
}



function ValidateEqual(txt1, txt2) {
    if (txt1.val().trim() == txt2.val().trim()) {
        return true;
    }
    else {
        return false;
    }
}

function ValidatePhoneNumber(lbl, txt) {
    var re = /^\+?[\d\s]{7,20}$/;
    if (!txt.val().trim().match(re)) {
        if (lbl != "")
            lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        if (lbl != "")
            lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateContactusPhoneNumber(lbl, txt) {
    var re = /^\+?\d{10,15}$/;
    if (!txt.val().trim().match(re)) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

//validate text for eng/arabic letters

function ValidateLetterText(txt) {
    var re = /[\u0600-\u06FF]|^[a-zA-Z]+$/;

    if (!txt.val().trim().match(re)) {
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        txt.removeClass(CssErrorClassName);
        return true;
    }

}

function ValidateLetterText(lbl, txt) {
    var re = /[\u0600-\u06FF ]|^[a-zA-Z ]+$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {

        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }

}

//validate Number field starts from 1 or 7 with limit of 0-10 digit 
function ValidateSponsorID(txt) {
    var re = /^[1|2|7][0-9]{9}$/;

    if (!txt.val().trim().match(re)) {
        txt.addClass(CssErrorClassName);
        return false;
    }
    else {
        txt.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateSponsorID(lbl, txt) {
    var re = /^[1|2|7][0-9]{9}$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateIDNumber(lbl, txt) {
    var re = /^[1|2|3|4][0-9]{0,9}$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {

        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateSaudiIDNumber(lbl, txt) {
    var re = /^[1][0-9]{0,9}$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        ValidateConfirmPassword

        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateExpatIDNumber(lbl, txt) {
    var re = /^[2][0-9]{0,9}$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {

        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateRegex(lbl, txt, regex) {
    var re = regex;
    if (!txt.val().trim().match(re)) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}








//function ValidateURL(lbl, txt) {
//    var regexp = /(ftp|http|https):\/\/(\w+:{0,1}\w*@)?(\S+)(:[0-9]+)?(\/|\/([\w#!:.?+=&%@!\-\/]))?/;
//    var regex = new RegExp(regexp);
//    if (!txt.val().trim().match(regex)) {
//        lbl.addClass(CssErrorClassName);
//        return false;
//    }
//    else {
//        lbl.removeClass(CssErrorClassName);
//        return true;
//    }
//}

function ValidateConfirmPassword(lblConfirmPass, txtPass, txtConfirmPass) {
    if (txtPass.val() != txtConfirmPass.val()) {
        lblConfirmPass.addClass(CssErrorClassName);
        return false;
    }
    else {
        lblConfirmPass.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateConfirmPasswordTxt(txtPass, txtConfirmPass) {
    if (txtPass.val() != txtConfirmPass.val()) {
        return false;
    }
    else {
        return true;
    }
}

function ValidateUploadFileContent(lbl, uploadControl) {
    if (uploadControl.val().trim().length == 0) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateTerms(chk) {
    if (!chk.is(":checked")) {
        //  chk.parent().addClass(CssErrorClassName);
        return false;
    }
    else {
        //  chk.parent().removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateCheckBox(lbl, chk) {
    if (!chk.is(":checked")) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function LabelAddError(lbl) {
    lbl.addClass(CssErrorClassName);
}

function LabelRemoveError(lbl) {
    lbl.removeClass(CssErrorClassName);
}

function ValidateRadio(lbl, array) {
    var isValid = false;

    if ($(array).is(':checked')) {
        lbl.removeClass(CssErrorClassName);
        isValid = true;
    }
    else {
        lbl.addClass(CssErrorClassName);
        isValid = false;
    }

    return isValid;
}

function ValidateNumber(lbl, txt) {

    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "") {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        isValid = false;
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        isValid = true;
        return true;
    }
}



function ValidateNumberWithPattern(lbl, txt) {
    var re = /^[0][5][0-9]{8}$/;

    if (!txt.val().trim().match(re)) {

        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}





////////

function ValidateNumberTxtOnly(txt) {
    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "") {
        isValid = false;
    }
    else {
        isValid = true;
    }
    return isValid;
}

function ValidateNumberTxt(lbl, txt) {
    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "") {
        if (lbl != "")
            lbl.addClass(CssErrorClassName);
        isValid = false;
    }
    else {
        if (lbl != "")
            lbl.removeClass(CssErrorClassName);
        isValid = true;
    }

    return isValid;
}
function ValidateNumberTxtNew(txt) {
    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "") {
        isValid = false;
    }
    else {
        isValid = true;
    }

    return isValid;
}


//Created to add error class on the parent span of the text box!
function ValidateNumberTextBox(txt) {
    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "") {
        txt.parent().addClass(CssErrorClassName);
        isValid = false;
    }
    else {
        txt.parent().removeClass(CssErrorClassName);
        isValid = true;
    }

    return isValid;
}

function ValidateFloat(lbl, txt) {
    var isValid = false;
    if (isNaN(parseFloat(txt.val().trim()))) {
        lbl.addClass(CssErrorClassName);
        isValid = false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        isValid = true;
    }

    return isValid;
}

function ValidateWaterMark(lbl, txt, validateText) {

    var isValid = false;
    if (txt.val() == validateText) {
        isValid = false;
        lbl.addClass(CssErrorClassName);
    }
    else {
        isValid = true;
        lbl.removeClass(CssErrorClassName);
    }

    return isValid;

}

function ValidateFileExtention(lbl, fileupload) {
    var isValid = false;
    var extention = fileupload.val().split('.');
    extention = extention[extention.length - 1];
    var types = [];
    types.push("mp4");
    types.push("mov");
    types.push("wmv");

    for (var i = 0; i < types.length; i++) {
        if (extention == types[i]) {
            isValid = true;
            lbl.removeClass(CssErrorClassName);
            return isValid;
        }
        else {
            isValid = false;
            lbl.addClass(CssErrorClassName);

        }
    }
    return isValid;
}

function CheckValidDateAndLeapYear(input, lbl) {

    var validformat = /^\d{2}\/\d{2}\/\d{4}$/;  //Basic check for format validity

    var returnval = false;

    if (!validformat.test(input))
        returnval = false;

    else {

        //Detailed check for valid date ranges

        var monthfield = input.split("/")[0];

        var dayfield = input.split("/")[1];

        var yearfield = input.split("/")[2];

        var dayobj = new Date(yearfield, monthfield - 1, dayfield);

        if ((dayobj.getMonth() + 1 != monthfield) || (dayobj.getDate() != dayfield) || (dayobj.getFullYear() != yearfield))
            returnval = false;

        else
            returnval = true
    }
    if (!returnval) {
        lbl.addClass(CssErrorClassName);
    }
    else {
        lbl.removeClass(CssErrorClassName);
    }
    return returnval
}

function isNumber(n) {
    return !isNaN(parseFloat(n)) && isFinite(n);
}

String.prototype.trim = function () {
    return this.replace(/^\s+|\s+$/g, "");
}

function ValidateAge(lbl, txt) {
    var isValid = false;
    if (isNaN(txt.val().trim()) || txt.val().trim() == "" || txt.val().trim() < 1) {
        lbl.addClass(CssErrorClassName);
        isValid = false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        isValid = true;
    }

    return isValid;
}

//function for validating alphabets only (both english and arabic)
function ValidateName(lbl, txt) {

    if (txt.valueOf().length > 0) {

        var regexp = /^[a-zA-Z\u0600-\u06FF ]+$/;

        if (!txt.val().trim().match(regexp)) {
            if (lbl != "") {
                lbl.addClass(CssErrorClassName);
            }
            return false;
        }
        else {
            if (lbl != "") {
                lbl.removeClass(CssErrorClassName);
            }
            return true;
        }
    }
    else {
        if (lbl != "") {
            lbl.addClass(CssErrorClassName);
        }
        return false;
    }
}

//function for validating all type of characters with limit of 300 characters
function ValidateMessage(lbl, txt) {

    if (txt.val().length > 0 && txt.val().length < 301) {

        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
    else {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
}






//new function added for restricting URLs in form detail fieds
function ValidateURLNew(lbl, txt) {

    var regexp = /(([a-z]+:\/\/)?(([a-z0-9\-]+\.)+([a-z]{2}|aero|arpa|biz|com|coop|edu|gov|info|int|jobs|mil|museum|name|nato|net|org|pro|travel|local|internal))(:[0-9]{1,5})?(\/[a-z0-9_\-\.~]+)*(\/([a-z0-9_\-\.]*)(\?[a-z0-9+_\-\.%=&amp;]*)?)?(#[a-zA-Z0-9!$&'()*+.=-_~:@/?]*)?)(\s+|$)/;
    var regex = new RegExp(regexp);
    if (txt.val().trim().match(regex)) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function ValidateURLStartEnd(lbl, txt) {

    var regexp = /\.aero|\.arpa|\.biz|\.com|\.coop|\.edu|\.gov|\.info|\.int|\.jobs|\.mil|\.museum|\.name|\.nato|\.net|\.org|\.pro|\.travel|\.local|\.internal|\www/;

    var regex = new RegExp(regexp);
    if (txt.val().trim().match(regex)) {
        lbl.addClass(CssErrorClassName);
        return false;
    }
    else {
        lbl.removeClass(CssErrorClassName);
        return true;
    }
}

function validatePreDate(lbl, txt) {

    //var CurrentDate = new Date("YYYY-MM-DD");
    var date = new Date();
    var currentDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
    var isValid = false;
    if (new Date(txt.val()) == 'Invalid Date') {
        isValid = false;
    }
    else {
        if (new Date(txt.val()) <= new Date(currentDate)) {

            isValid = true;
        }
        else {

            isValid = false;
        }
    }

    return isValid;
}

function validatePreDateDependent(lbl1, lbl2, lbl3, txt) {

    //var CurrentDate = new Date("YYYY-MM-DD");
    var date = new Date();
    var currentDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
    var isValid = false;
    if (new Date(txt.val()) == 'Invalid Date') {
        lbl3.hide();
        lbl2.show();
        isValid = false;
    }
    else {
        if (new Date(txt.val()) <= new Date(currentDate)) {
            lbl3.hide();
            lbl2.show();
            isValid = false;
        }
        else {
            lbl2.hide();
            isValid = true;
        }
    }

    return isValid;
}

function validateDateDependent(lbl1, lbl2, lbl3, txt) {

    //var CurrentDate = new Date("YYYY-MM-DD");
    var date = new Date();
    var currentDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
    var isValid = false;
    if (new Date(txt.val()) == 'Invalid Date') {
        lbl3.hide();
        lbl2.show();
        isValid = false;
    }
    else {
        lbl2.hide();
        isValid = true;
    }

    return isValid;
}

function validatePostDate(lbl, txt) {

    //var CurrentDate = new Date("YYYY-MM-DD");
    var date = new Date();
    var currentDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
    var isValid = false;
    if (new Date(txt.val()) == 'Invalid Date') {
        isValid = false;
    }
    else {
        if (new Date(txt.val()) >= new Date(currentDate)) {

            isValid = true;
        }
        else {

            isValid = false;
        }
    }

    return isValid;
}

function validatePostDateDependent(lbl1, lbl2, lbl3, txt) {

    //var CurrentDate = new Date("YYYY-MM-DD");
    var date = new Date();
    var currentDate = (date.getMonth() + 1) + '/' + date.getDate() + '/' + date.getFullYear();
    var isValid = false;
    if (new Date(txt.val()) == 'Invalid Date') {
        lbl3.hide();
        lbl2.show();
        isValid = false;
    }
    else {
        if (new Date(txt.val()) >= new Date(currentDate)) {
            lbl3.hide();
            lbl2.show();
            isValid = false;
        }
        else {
            lbl2.hide();
            isValid = true;
        }
    }

    return isValid;
}

function validateAlphanumeric(lbl, txt) {
    var alphanumericPattern = /^[0-9a-zA-Z]+$/;
    if ((txt.val().match(alphanumericPattern))) 
    {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
    else
    {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
}

function validateNumeric(lbl, txt) {
    if (!isNaN(txt.val())) 
    {
        lbl.removeClass(CssErrorClassName);
        txt.removeClass(CssErrorClassName);
        return true;
    }
    else
    {
        lbl.addClass(CssErrorClassName);
        txt.addClass(CssErrorClassName);
        return false;
    }
}