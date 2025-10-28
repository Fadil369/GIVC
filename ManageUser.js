function HideCaptchaMessage() {
    document.getElementById(WrongCaptcha.id).style.display = "none";
}
function LinktoggleFooter() {
    if ($('#TermsAndLinks').hasClass('RemoveWidth')) {
        $('#TermsAndLinks').removeClass('RemoveWidth');
        $('#TermsAndLinks').addClass('Addwidth');
		document.getElementById(divReadMore.id).innerText = "Read More";
		document.getElementById(divArReadMore.id).innerText = "أقراالمزيد";
    }
    else {
        $('#TermsAndLinks').removeClass('Addwidth');
        $('#TermsAndLinks').addClass('RemoveWidth');
		document.getElementById(divReadMore.id).innerText = "Read Less";
		document.getElementById(divArReadMore.id).innerText = "قراءه اقل";
    }
}
function HideUserExistSpan() {
    document.getElementById(ReqUserExist.id).style.display = "none";
}
$(function () {
    $('#slider,#Helpslider').anythingSlider();
});