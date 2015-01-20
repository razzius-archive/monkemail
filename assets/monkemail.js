var clearPopup = function(){
    var overlay = document.getElementById('monkemail_overlay');
    overlay.parentNode.removeChild(overlay);
    var popup = document.getElementById('monkemail_popup');
    popup.parentNode.removeChild(popup);
};

var send_email = function() {
    var from_email = document.getElementById('monkemail_email_input').value;
    var content = document.getElementById('monkemail_message').value;

    var payload = {
        from_email: from_email,
        content: content,
        website_url: window.location.host
    };

    var request = new XMLHttpRequest();
    request.open('POST', 'http://api.monkemail.me/contact/', true);
    request.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    var resp = request.send(JSON.stringify(payload));
    clearPopup();
};

var showPopup = function() {
    var overlay = document.createElement('div');
    overlay.id = 'monkemail_overlay';
    var body = document.body;
    body.insertBefore(overlay, body.firstChild);
    var popup = document.createElement('div');
    popup.id = 'monkemail_popup';
    popup.className = 'monkemail';
    popup.innerHTML =
        '<div id="monkemail_header">' +
        '    <div id="monkemail_close_button">x</div>' +
        '    <h2 id="monkemail_title">Contact us</h2>' +
        '</div>' +
        '<div id="monkemail_body">' +
        '    <form class="monkemail">' +
        '        <h3 class="monkemail_prompt">Your Email</h3>' +
        '        <input id="monkemail_email_input" type="email">' +
        '        <h3 class="monkemail_prompt">Message</h3>' +
        '        <textarea id="monkemail_message"></textarea>' +
        '        <span id="monkemail_submit">Submit</span>' +
        '    </form>' +
        '</div>';

    body.appendChild(popup);
    var close_button = document.getElementById('monkemail_close_button');
    close_button.addEventListener('click', clearPopup);
    overlay.addEventListener('click', clearPopup);
    var submit = document.getElementById('monkemail_submit');
    submit.addEventListener('click', send_email);
};

document.getElementById('monkemail_contact').addEventListener('click', showPopup);
