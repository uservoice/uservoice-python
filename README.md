UserVoice Python module for API connections
===========================================

This library allows you to easily:
* Generate SSO token for creating SSO users / logging them into UserVoice (http://uservoice.com).
* Do 3-legged and 2-legged UserVoice API calls safely without having to worry about the cryptographic details (unless you want).

Examples
========

Prerequisites:
* Suppose your UserVoice site is at http://uservoice-subdomain.uservoice.com/ and **USERVOICE\_SUBDOMAIN** = uservoice-subdomain
* **SSO\_KEY** = 982c88f2df72572859e8e23423eg87ed (Admin Console -> Settings -> General -> User Authentication)
* The account has a following API client (Admin Console -> Settings -> Channels -> API):
    * **API\_KEY** = oQt2BaunWNuainc8BvZpAm
    * **API\_SECRET** = 3yQMSoXBpAwuK3nYHR0wpY6opE341inL9a2HynGF2

SSO-token generation using uservoice gem
----------------------------------------

SSO-token can be used to create sessions for SSO users. They are capable of synchronizing the user information from one system to another.
Generating the SSO token from SSO key and given uservoice subdomain can be done by calling UserVoice.generate\_sso\_token method like this:

```python
import uservoice

sso_token = uservoice.generate_sso_token(USERVOICE_SUBDOMAIN, SSO_KEY, {
    'guid': 1000000,
    'display_name': "User Name",
    'email': 'mailaddress@example.com'
})

print "https://uservoice-subdomain.uservoice.com/?sso=" + sso_token
```


Making 2-Legged API calls
-------------------------

Managing backups and extracting all the users of a UserVoice subdomain are typical use cases for making 2-legged API calls. With the help
of the gem you just need to create an instance of UserVoice::Oauth (needs an API client, see Admin Console -> Settings -> Channels -> API).
Then just start making requests like the example below demonstrates.

```python
import uservoice
import simplejson as json

oauth = uservoice.OAuth(USERVOICE_SUBDOMAIN, API_KEY, API_SECRET)
users = json.load(oauth.request('get', "/api/v1/users.json"))
for user_hash in users['users']:
    print 'User: "' + user_hash['name'] + '", Profile URL: ' + user_hash['url']
```

Making 3-Legged API calls
-------------------------

If you want to make calls on behalf of a user, you need 3-legged API calls. It basically requires you to pass a link to UserVoice, where
user grants your site permission to access his or her data in his or her account

```python
import uservoice
import simplejson as json

CALLBACK_URL = 'http://localhost:3000/' # This represents the URL you want UserVoice send you back

oauth = uservoice.OAuth(USERVOICE_SUBDOMAIN, API_KEY, API_SECRET, callback=CALLBACK_URL)

print "1. Go to " + oauth.authorize_url() + " and click \"Allow access\"."
print "2. Then type the oauth_verifier which is passed as a GET parameter to the callback URL:"

oauth.get_access_token(verifier=raw_input().strip())

user = json.load(oauth.request('get', "/api/v1/users/current.json"))['user']

print 'User: "' + user['name'] + '", Profile URL: ' + user['url']
```