/**************************************** Footer Funtion  ********************************/
function toggleFooter() {
    $('#footerLinks').slideToggle();
    $('#footerLink').toggleClass('active');
}

/****************************************Drop Down & Rollover Menu  ********************************/
function MM_swapImgRestore() {
    var i, x, a = document.MM_sr; for (i = 0; a && i < a.length && (x = a[i]) && x.oSrc; i++) x.src = x.oSrc;
}

function MM_swapImage() {
    var i, j = 0, x, a = MM_swapImage.arguments; document.MM_sr = new Array; for (i = 0; i < (a.length - 2); i += 3)
        if ((x = MM_findObj(a[i])) != null) { document.MM_sr[j++] = x; if (!x.oSrc) x.oSrc = x.src; x.src = a[i + 2]; }
}

function MM_findObj(n, d) {
    var p, i, x; if (!d) d = document; if ((p = n.indexOf("?")) > 0 && parent.frames.length) {
        d = parent.frames[n.substring(p + 1)].document; n = n.substring(0, p);
    }
    if (!(x = d[n]) && d.all) x = d.all[n]; for (i = 0; !x && i < d.forms.length; i++) x = d.forms[i][n];
    for (i = 0; !x && d.layers && i < d.layers.length; i++) x = MM_findObj(n, d.layers[i].document);
    if (!x && d.getElementById) x = d.getElementById(n); return x;
}

function MM_showHideLayers() {
    var i, p, v, obj, args = MM_showHideLayers.arguments;
    for (i = 0; i < (args.length - 2); i += 3) if ((obj = MM_findObj(args[i])) != null) {
        v = args[i + 2];
        if (obj.style) { obj = obj.style; v = (v == 'show') ? 'visible' : (v == 'hide') ? 'hidden' : v; }
        obj.visibility = v;
    }
}


/************************************** Menu Positioning *************************************/
var main_table_width = 995;

function adjustOverlayPosition(div) {
    //alert($(div).offset().left)
    $(div).css("left", -1);  //reset
    //var page_offset = $("#sizer").offset().left;
    var page_offset = ($(window).width() - 995) / 2
    if ($(div).offset()) {
        var left = $(div).offset().left - page_offset;
        var w = $(".absoluteTopSubMenu").width();
        var right_diff = (left + w) - main_table_width;
        if (right_diff > 0) {
            $(div).css("left", $(div).position().left - right_diff - 22);
            //$(".AbsoluteSubCont", $(div)).css("left", -160);	// aligning sub menus
        }
    }
}

$(document).ready(function () {
    //adjustOverlayPosition('.absoluteTopSubMenu')
    //adjustOverlayPosition('#sub1');
    adjustOverlayPosition('#sub2');
    adjustOverlayPosition('#sub3');
    adjustOverlayPosition('#sub4');
    adjustOverlayPosition('#sub5');
    adjustOverlayPosition('#sub6');
    adjustOverlayPosition('#sub7');

    $(".myNeedToDropdown").change(function () {
        var valueCatched = $(this).val()
        if (valueCatched == "0") {
            return false;
        }
        if ($('option:selected', $(this)).attr('external') == "true") {
            window.open(valueCatched);
        }
        else {
            window.location = valueCatched;
        }
        return false;
    });

})

function gototop() { alert('hi'); $('#anchor1').click() }

//  Chat Popup Window
function OpenChatWindow( url)
{
 var width  = 400;
 var height = 270;
 var left   = (screen.width  - width)/2;
 var top    = (screen.height - height)/2;
 var params = 'width='+width+', height='+height;
 params += ', top='+top+', left='+left;
 params += ', directories=no';
 params += ', location=no';
 params += ', menubar=no';
 params += ', resizable=no';
 params += ', scrollbars=no';
 params += ', status=no';
 params += ', toolbar=no';
 newwin=window.open(url,'windowname5', params);
 if (window.focus) {newwin.focus()}
 return false;
}

function validateNumber(evt) {
    var theEvent = evt || window.event;

    // Handle paste
    if (theEvent.type === 'paste') {
        key = event.clipboardData.getData('text/plain');
    } else {
        // Handle key press
        var key = theEvent.keyCode || theEvent.which;
        key = String.fromCharCode(key);
    }
    var regex = /^\d+$/;
    if (!regex.test(key)) {
        theEvent.returnValue = false;
        if (theEvent.preventDefault) theEvent.preventDefault();
    }
}

