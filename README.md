Monkemail is an email plugin for websites.

<img src="screenshot.png">

[Demo][http://monkemail.github.io]

Tired of `mailto` links? Want a good user experience for your contact page?


## Register for Monkemail

Head to [monkemail.me] and sign up using your Github account. It's free! Take note of your API token.


## Install Monkemail

Add the following line of code to your website

    <a id="monkemail_contact">Contact Us</a>
    <script type="text/javascript">
        var monkemail_name = 'monkemailme'; // required: replace example with your forum shortname

        /* * * DON'T EDIT BELOW THIS LINE * * */
        (function() {
            var dsq = document.createElement('script'); dsq.type = 'text/javascript'; dsq.async = true;
            dsq.src = '//' + disqus_shortname + '.disqus.com/embed.js';
            (document.getElementsByTagName('head')[0] || document.getElementsByTagName('body')[0]).appendChild(dsq);
        })();
    </script>
    <noscript>Please enable JavaScript to view the <a href="https://disqus.com/?ref_noscript">comments powered by Disqus.</a></noscript>


## Options

There are 2 kinds of email integrations you can enable:

- contact us
- share
