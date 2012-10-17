import mechanize as mech
import os
import sys
import urllib2

# Instantiate a Browser
browser = mech.Browser()

# Build the URI I need
uri =  'https://www.facebook.com/dialog/oauth?'
uri += 'client_id=103806206443210'
uri += '&redirect_uri=http://chriswald.com/facebash.htm'
uri += '&scope=user_about_me,friends_about_me,friends_birthday,user_likes,friends_likes,user_relationships,friends_relationships,user_status,friends_status,publish_stream,read_stream'
uri += '&response_type=token'

# Pretend I'm not a bot by creating a cookie cache and setting the
# user agent to one of a common web browser.
browser.set_handle_robots(False)
cookies = mech.CookieJar()
browser.set_cookiejar(cookies)
browser.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US) AppleWebKit/534.7 (KHTML, like Gecko) Chrome/7.0.517.41 Safari/534.7')]


# Now is the complicated part. I need to determine how the login went
# based on which page I'm redirected to. There are three know options:
#
# Base: facebook.com/dialog/oauth
#    1: chriswald.com/facebash.htm
#    2: facebook.com/login.php
#    3: facebook.com/dialog/permissions.request
#
# 1: chriswald.com/facebash.htm
# =============================
#
# This page is the ultimate goal of the process because it will be
# passed the authentification token and expiration time. This page
# will be reached from either (Base) or (3). If no new permissions are
# requested and the login is successful the flow will be
#                 (Base) --> (1)
# If new permissions are requested the flow will be
#                 (Base) --> (3) --> (1)
#
#
# 2: facebook.com/login.php
# =========================
#
# This page is only requested if the login failed. If I end up here it
# means that the user entered an invalid username (email address) or
# password. The flow of pages would be
#                 (Base) --> (2) -------> (1)
#                             ^   /\       ^
#                             |__/  \      |
#                                    `--> (3)
#
# (2) can be returned any number of times until the user enters valid
# login information, but then can branch to either of the two pages,
# (1) or (3). If no new permissions are requested then (1) will be
# branched to, otherwise (3) will be requested, followed by (1).
#
#
# 3: facebook.com/dialog/permissions.request
# ==========================================
#
# This page is only requested for a new user or if the application's
# permissions have changed. It can follow either (Base) or (2), based
# on the rules defined in section 2, pertaining to a successful login.
#                (Base) --> (3)
#
#                (Base) --> (2) --> (3)
#
#
# Full Lifecycle:
# ===============
#                 (Base) --> (2) -------> (1)
#                             ^   /\       ^
#                             |__/  \      |
#                                    `--> (3)
#
# Return Values:
# ==============
#
# {token | 1 | 2 | 3}
#
# If the token is returned the operation was successful. Returning a 1
# means that the email or password provided was incorrect. A 2 means
# that the user denied your app permissions. A 3 means that some other
# error occured.
#


# This is where the magic happens
# Open the URI, fill out the forms and submit everything
return_val = ''
url = ''

try:
    browser.open(uri)
    browser.select_form(nr=0)
    browser['email'] = sys.argv[1]
    browser['pass'] = sys.argv[2]
    response1 = browser.submit(name='login', label='Log In')

    url = response1.geturl()
except urllib2.URLError:
    return_val = '3'

if 'login.php' in url:
    return_val = '1'
else:
    # If we were redirected to a facebook site ask the user for permission to
    # add this application to their trusted list.
    if 'permissions.request' in url:
        sys.stdout.write('Do you want to grant this app permissions to your Facebook account? (y or n): ')
        answer = str(raw_input())
        if answer == 'Y' or answer == 'y':
            browser.select_form(nr=2)
            response1 = browser.submit(nr=0)
            url = response1.geturl()
        else:
            return_val = '2'

    if '#' in url and '&' in url:
        POSTS = url[url.index('#')+1:]
        parts = POSTS.split('&')
        auth_token = parts[0].split('=')[1]
        return_val = auth_token
    else:
        return_val = '3'

try:
    os.remove('member27')
except OSError:
    pass

f = open('member27', 'w+')
f.write(return_val + '\n')
f.close()
