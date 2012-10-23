UserVoice Python module for API connections
===========================================

This library allows you to easily:
* Generate SSO token for creating SSO users / logging them into UserVoice (http://uservoice.com).
* Do 3-legged and 2-legged UserVoice API calls safely without having to worry about the cryptographic details (unless you want).

Installation
============

Use pip to install the uservoice Python module:

```sh
pip install uservoice
```

Now you should be good to go!

Examples
========

Prerequisites:
* Suppose your UserVoice site is at http://uservoice-subdomain.uservoice.com/ and **USERVOICE\_SUBDOMAIN** = uservoice-subdomain
* **SSO\_KEY** = 982c88f2df72572859e8e23423eg87ed (Admin Console -> Settings -> General -> User Authentication)
* The account has a following API client (Admin Console -> Settings -> Channels -> API):
    * **API\_KEY** = oQt2BaunWNuainc8BvZpAm
    * **API\_SECRET** = 3yQMSoXBpAwuK3nYHR0wpY6opE341inL9a2HynGF2

SSO-token generation using the uservoice python library
-------------------------------------------------------

SSO-token can be used to create sessions for SSO users. They are capable of synchronizing the user information from one system to another.
Generating the SSO token from SSO key and given uservoice subdomain can be done by calling UserVoice.generate\_sso\_token method like this:

```python
import uservoice

sso_token = uservoice.generate_sso_token(USERVOICE_SUBDOMAIN, SSO_KEY, {
    'guid': 1000000,
    'display_name': "User Name",
    'email': 'mailaddress@example.com'
})

print "https://" + USERVOICE_SUBDOMAIN + ".uservoice.com/?sso=" + sso_token
```


Making API calls
----------------

With the gem you need to create an instance of uservoice.Client. You get
API_KEY and API_SECRET from an API client which you can create in Admin Console
-> Settings -> Channels -> API.

```python
import uservoice
try:
    client = uservoice.Client(USERVOICE_SUBDOMAIN, API_KEY, API_SECRET)

    # Get users of a subdomain (requires trusted client, but no user)
    users = client.get("/api/v1/users")['users']
    for user in users:
      print 'User: "{name}", Profile URL: {url}'.format(**user)

    # Now, let's login as mailaddress@example.com, a regular user
    with client.login_as('mailaddress@example.com') as regular_access_token:
        # Example request #1: Get current user.
        user = regular_access_token.get("/api/v1/users/current")['user']

    print 'User: "{name}", Profile URL: {url}'.format(**user)

    # Login as account owner
    owner_access_token = client.login_as_owner()

    # Example request #2: Create a new private forum limited to only example.com email domain.
    forum = owner_access_token.post("/api/v1/forums", {
        'forum': {
            'name': 'Example.com Private Feedback',
            'private': True,
            'allow_by_email_domain': True,
            'allowed_email_domains': [{'domain': 'example.com'}]
        }
     })['forum']

    print 'Forum "{name}" created! URL: {url}'.format(**forum)
except uservoice.Unauthorized as e:
    # Thrown usually due to faulty tokens, untrusted client or if attempting
    # operations without Admin Privileges
    print e
except uservoice.NotFound as e:
    # Thrown when attempting an operation to a resource that does not exist
    print e
```

Verifying a UserVoice user
--------------------------

If you want to make calls on behalf of a user, but want to make sure he or she
actually owns certain email address in UserVoice, you need to use 3-Legged API
calls. Just pass your user an authorize link to click, so that user may grant
your site permission to access his or her data in UserVoice.

```python
import uservoice
CALLBACK_URL = 'http://localhost:3000/' # your site

client = uservoice.Client(USERVOICE_SUBDOMAIN, API_KEY, API_SECRET, callback=CALLBACK_URL)

# At this point you want to print/redirect to client.authorize_url in your application.
# Here we just output them as this is a command-line example.
print "1. Go to {url} and click \"Allow access\".".format(url=client.authorize_url())
print "2. Then type the oauth_verifier which is passed as a GET parameter to the callback URL:"

# In a web app we would get the oauth_verifier via a redirection to CALLBACK_URL.
# In this command-line example we just read it from stdin:
access_token = client.login_with_verifier(raw_input())

# All done. Now we can read the current user to know user's email address:
user = access_token.get("/api/v1/users/current")['user']
print "User logged in, Name: {name}, email: {email}".format(**user)
```
