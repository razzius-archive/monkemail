serialize = function(obj) {
   var str = [];
   for(var p in obj){
       if (obj.hasOwnProperty(p)) {
           str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
       }
   }
   return str.join("&");
};

var BASE_OAUTH_URL = 'https://github.com/login/oauth/authorize?';

var get_parameters = {
    client_id: '72e93ca6dc8ad6c3fb67',
    redirect_uri: 'http://api.monkemail.me/oauth',
    scope: 'user:email',
    state: Math.random().toString(36).substring(7)
};


var signup = document.getElementById('signup');
signup.href = BASE_OAUTH_URL + serialize(get_parameters);


