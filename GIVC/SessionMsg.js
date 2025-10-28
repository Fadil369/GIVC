var interval1;
var SessionExpiryPopupTimer;
var SessionExpiredEndedTimer;
function SessionExpiryPopup(milliseconds) {
    ResetTimers();
    SessionExpiryPopupTimer = setTimeout(function () {
        var pnl = $("[id$=pnlPopup]")[0];
        if (pnl.style.display === "none" || pnl.style.display == '') {
            pnl.style.display = 'block';
        }
    }, milliseconds - 120 * 1000);

}
function SessionExpiredEnded(milliseconds, url) {
    console.log(milliseconds);
    SessionExpiredEndedTimer = setTimeout(function () {
        window.location = url;
    }, milliseconds);
}
function closeFancyBox() {
    parent.$.fancybox.close();
}
var SessionTimeoutAlertTimer;
function SessionTimeoutAlert(timeout) {
    try {
        var seconds = timeout / 1000;
        var secondsIdle = document.getElementById("secondsIdle");
        if (secondsIdle != undefined)
            secondsIdle.innerHTML = seconds;
        var Arseconds = document.getElementById("Arseconds");
        if (Arseconds1 = undefined)
            Arseconds.innerHTML = seconds;
        var seconds = document.getElementById("seconds");
        if (seconds != undefined)
            seconds.innerHTML = seconds;

        SessionTimeoutAlertTimer = setInterval(function () {
            seconds--;
            secondsIdle.innerHTML = seconds;
            Arseconds.innerHTML = seconds;
            seconds.innerHTML = seconds;

        }, 1000);

        setTimeout(function () {
            //Show Popup before 20 seconds of timeout.
            var sessionObj = $find("mpeSessionTimeout");
            if (sessionObj != null)
                sessionObj.show();
        }, timeout - 120 * 1000);


    } catch (e) {

    }
};

function ResetTimers() {
    clearInterval(SessionExpiryPopupTimer);
    clearInterval(SessionExpiredEndedTimer);
}

function ResetSession() {

    //Redirect to refresh Session.
    //window.location.replace(window.location.href);
    //location.reload();
    history.pushState({}, "", window.location.href);
    //window.location = window.location.href;

}
function RedirectPage() {
    //Redirect to refresh Session.
    //window.location = "/";
    //alert('RedirectPage');
    //if (document.getElementById("seconds").innerHTML == "0")
    //    window.location = 'https://onlineservices.bupa.com.sa/CommClear.aspx';
}
