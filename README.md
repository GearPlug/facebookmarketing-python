# facebookmarketing-python

facebookmarketing is an API wrapper for Facebook and Instagram written in Python.

## Installing
```
pip install facebookmarketing-python
```

## Facebook Usage

#### Client instantiation
```
from facebookmarketing.client import Client

client = Client('APP_ID', 'APP_SECRET', 'v4.0')
```

### OAuth 2.0

For more information: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/

#### Get authorization url
```
url = client.authorization_url('REDIRECT_URL', 'STATE', ['pages_manage_ads', 'pages_manage_metadata', 'pages_read_engagement', 'leads_retrieval'])
```

#### Exchange the code for an access token
```
response = client.exchange_code('REDIRECT_URL', 'CODE')
access_token = response['access_token']
```

#### Extend a short-lived access token for a long-lived access token
```
response = client.extend_token(access_token)  # From previous step
access_token = response['access_token']
```

#### Get app token
```
response = client.get_app_token()
app_access_token = response['access_token']
```

#### Inspect a token
```
response = client.inspect_token(access_token, app_access_token)  # From previous step
```

#### Set the access token in the library
```
client.set_access_token(access_token)  # From previous step
```

### User

For more information: https://developers.facebook.com/docs/graph-api/reference/user/

#### Get account information
```
response = client.get_account()
```

#### Get account pages
```
response = client.get_pages()
```

#### Get page token
```
page_access_token = client.get_page_token('PAGE_ID')  # From previous step
```

### Page

For more information: https://developers.facebook.com/docs/graph-api/reference/page/

#### Get lead generation forms given the page
```
response = client.get_ad_account_leadgen_forms('PAGE_ID', page_access_token)  # From previous step
```
#### Get leads info given the lead generation form
```
response = client.get_ad_leads('LEADGEN_FORM_ID')
```

#### Get a sigle lead info
```
response = client.get_leadgen('LEADGEN_ID')
```

### Webhooks

For more information: https://developers.facebook.com/docs/graph-api/webhooks

The following methods cover Step 2 and 4 of the Webhook lead retrieval guide:
Webhooks: https://developers.facebook.com/docs/marketing-api/guides/lead-ads/retrieving/

#### Create a webhook for leads retrieval
```
response = client.create_app_subscriptions('page', 'callback_url', 'leadgen', 'abc123', app_access_token)  # You get app_access_token from get_app_token() method

response = client.create_page_subscribed_apps('PAGE_ID', page_access_token, params={'subscribed_fields': 'leadgen'})  # You get page_access_token from get_page_token() method
```

## Instagram Usage

#### Client instantiation
```
from facebookmarketing.client import Client

client = Client('APP_ID', 'APP_SECRET', 'v12.0')
```

### OAuth 2.0

For more information: https://developers.facebook.com/docs/facebook-login/manually-build-a-login-flow/

#### Get authorization url
```
url = client.authorization_url('REDIRECT_URL', 'STATE', ['instagram_basic', 'pages_show_list'])
```

#### Exchange the code for an access token
```
response = client.exchange_code('REDIRECT_URL', 'CODE')
access_token = response['access_token']
```

### Page

#### Get page id
```
response = client.get_instagram(page_id, ['instagram_business_account'])
page_id = response['instagram_business_account']['id']
```

### Media

#### Get media
```
response = client.get_instagram_media(page_id)
```

#### Get media object
```
response = client.get_instagram_media_object(media_id, fields=['id','media_type','media_url','owner','timestamp'])
```

### Hashtag

#### Search hashtag
```
response = (client.get_instagram_hashtag_search(page_id, 'coke'))
```

#### Get hashtag object
```
response = client.get_instagram_hashtag_object(hashtag_id, fields=['id', 'name']) 
```

#### Get hashtag top media
```
response = client.get_instagram_hashtag_top_media(hashtag_id, instagram_id, ['id','media_type','comments_count','like_count', 'caption'])
```

## Requirements
- requests

## Contributing
We are always grateful for any kind of contribution including but not limited to bug reports, code enhancements, bug fixes, and even functionality suggestions.

#### You can report any bug you find or suggest new functionality with a new [issue](https://github.com/GearPlug/facebookmarketing-python/issues).

#### If you want to add yourself some functionality to the wrapper:
1. Fork it ( https://github.com/GearPlug/facebookmarketing-python )
2. Create your feature branch (git checkout -b my-new-feature)
3. Commit your changes (git commit -am 'Adds my new feature')
4. Push to the branch (git push origin my-new-feature)
5. Create a new Pull Request
