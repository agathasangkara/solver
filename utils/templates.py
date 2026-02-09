HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>body's solver</title>
    <script src="https://challenges.cloudflare.com/turnstile/v0/api.js?onload=onloadTurnstileCallback" async="" defer=""></script>
</head>
<body>
    <!-- cf turnstile -->
    <p id="ip-display"></p>
</body>
</html>
"""

RECAPTCHA_V3_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>reCAPTCHA v3 Solver</title>
    <script src="https://www.google.com/recaptcha/api.js?render={sitekey}"></script>
</head>
<body>
    <input type="hidden" id="recaptcha-token" name="recaptcha-token">
    <script>
        grecaptcha.ready(function() {{
            grecaptcha.execute('{sitekey}', {{action: '{action}'}}).then(function(token) {{
                document.getElementById('recaptcha-token').value = token;
            }});
        }});
    </script>
</body>
</html>
"""

RECAPTCHA_V2_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>reCAPTCHA v2 Solver</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body>
    <div class="g-recaptcha" data-sitekey="{sitekey}" data-callback="onSuccess"></div>
    <input type="hidden" id="recaptcha-response">
    <script>
        function onSuccess(token) {{
            document.getElementById('recaptcha-response').value = token;
        }}
    </script>
</body>
</html>
"""

RECAPTCHA_V2_INVISIBLE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>reCAPTCHA v2 Invisible</title>
    <script src="https://www.google.com/recaptcha/api.js" async defer></script>
</head>
<body>
    <div class="g-recaptcha" data-sitekey="{sitekey}" data-size="invisible" data-callback="onSuccess"></div>
    <input type="hidden" id="recaptcha-response">
    <script>
        function onSuccess(token) {{
            document.getElementById('recaptcha-response').value = token;
        }}
        setTimeout(function() {{ grecaptcha.execute(); }}, 1000);
    </script>
</body>
</html>
"""