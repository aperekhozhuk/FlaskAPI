# Simple REST API on Flask. It provides backend for simple forum.

## Now it uses SQlite for DB and SQlAlchemy for ORM
Ability:
1. User registration - only username and password fields, no email confirmation
2. Simple Authentication based on JWT
3. Getting last (by date_posted) articles (or also of specified user) by pages, or just single specified article
4. Creating, Updating or Deleting own articles - only for registered users
5. Geting user's public data (profile) by id. Now it's just username and date of registration
6. Verifying client's access-token

# Running locally
1. Clone && cd into repository folder
2. Create virtual environment called 'env' (because actually this name I'm using in .gitignore)
3. Run 'pip install -r requirements.txt'
4. Run 'flask db upgrade' - creating DB
5. Run 'flask run'
6. It's available on localhost:5000 (by default)

# Testing
You need to run your app (in other window or in background) and then run testing script. Testing is going on with temporarry DB. Your main DB (which stores in 'db.sqlite') stays unchanged
1. Run 'flask run'
2. Run 'python tests.py -v'

# Api endpoints:

Routes 3), 4), 5), 10) demand from client 'access-token' field, passed in body of request.
You can get valid token if login with correct username and password.
In case of invalid access-token you will get:
```
{
  "error": "Invalid access-token. Log in please"
}, status = 401
```
In case of token missing:
```
{
  "error": "Access-token is missing. Log in, please"
}, status = 401
```

### 1. GET '/articles?page={n}' - get last articles
Returns last articles. If 'page' parameter passed - return specific page.
Max count of articles per page specified in project settings.
Also returns bool value, which tell if next page exists. <br>
Response:
```
{
  "articles":
    [
      {
        "id": 1,
        "date_posted": "2020-02-02T00:17:49.735642",
        "title": "Text 1",
        "user_id": 1,
        "author.username": "username_axample"
      },
      {
        "id": 2,
        "date_posted": "2020-02-02T00:17:49.735642",
        "title": "Text 2",
        "user_id": 1,
        "author.username": "username_axample"
      }
    ],
  "next" : false
}, status = 200
```
or empty list if no articles, also status = 200

### 2. GET '/articles/**{id}**' - return article with specified id
Response:
```
{
  "id": 1,
  "text": "Hello world, edited",
  "title": "1st articlem edited",
  "date_posted": "2020-02-02T00:17:49.735642",
  "user_id": 1,
  "author.username": "username_axample"
}, status = 200
```
or if article was not found:
```
{
  "error": "Article with id={id} was not found"
}, status = 404
```
### 3. POST '/articles/new' - create new article and return it
Headers:
```
Content-Type: application/json
```
Body:
```
{
	"title": "New article title",
	"text": "New article text",
	"access-token":"access.token.example"
}
```
Response:
```
{
  "date_posted": "2020-02-04T03:46:04.264139",
  "id": 24,
  "text": "Hello world, firstly",
  "title": "2nd article",
  "user_id": 1
}, status = 200
```
In case of title missing:  (for text missing - same)
```
{
  "error": "Article text is missing"
}, status = 400
```
### 4. PUT '/articles/**{id}**/edit' - update article with specified id & return updated article
Headers, Body, Response - same as 3), but also <br>
If article was not found:
```
{
  "error": "Article with id=222 was not found"
}, status = 404
```
If you'll try to delete not own post:
```
{
  "error": "You can edit only own article"
}, status = 403
```
### 5. DELETE '/articles/**{id}**/delete' - delete article with specified id & return deleted article
Headers:
```
Content-Type: application/json
```
Body:
```
{
  "access-token": "json.token.example"
}
```
If article was not found or If you'll try to delete not own post - same as 4).
### 6. POST '/register'  - register new user
#### Constraints:
```
Username:
  5 <= length <= 20
  allowed symbols:
    spec symbols: '!', '@', '#', '$', '%', '^', '&', '*', '-', '_',
    digits,
    english letters (upper case and lower case)

Password:
  8 <= length <= 40
  allowed symbols - same as for Username
  additional constraints: 1 lower case, 1 uppercase, 1 digit, 1 specsymbol
```
Headers:
```
Content-Type: application/json
```
Body:
```
{
	"username": "username_axample",
	"password": "password_example"
}
```
Response:
```
{
  "date_registered": "2020-02-04T04:04:54.627786",
  "id": 5,
  "username": "username_example"
}, status = 200
```
In case of username missing (for password - the same) 
```
{'
  error': 'Username is missing'
}, status = 400
```
In case when username already used:
```
{
  "error": "User with such username already exists"
}, status = 409
```
In case when username breaks constraints (for password - the same):
```
{
  "error": "Bad username format"
}, status = 400
```
### 7. POST '/login' - log in as registered user
Headers:
```
Content-Type: application/json
```
Body:
```
{
	"username": "username_axample",
	"password": "password_example"
}
```
Response:
```
{
  "access-token": "returned.token.example",
  "user_id": 1,
  "username": "username_axample"
}, status = 200
```
Or
```
{
  "error": "Uncorrect username or/and password"
}, status = 401
```
Or - when username is missing (for password - the same)
```
{
  "error": "Username is missing"
}, status = 400
```
### 8. GET '/users/{id}' - get user profile

Response:
```
{
  "date_registered": "2020-02-02T00:17:25.387019",
  "id": 1,
  "username": "username_axample"
}, status = 200
```
or if user with such id doesn't exist
```
{
  "error": "User with id={id} was not found"
}, status = 404
```
### 9. GET '/users/{id}/articles?page={n}' - get last user's articles
Same as 1), but returns articles of specified user. <br>
Response:
```
{
  "articles":
    [
      {
        "date_posted": "2020-02-04T03:48:45.259224",
        "id": 25,
        "title": "2nd article",
        "user_id": 1,
        "author.username": "username_axample"
      },
      {
        "date_posted": "2020-02-04T03:46:04.264139",
        "id": 24,
        "title": "2nd article",
        "user_id": 1,
        "author.username": "username_axample"
      },
      {
        "date_posted": "2020-02-04T03:44:40.030282",
        "id": 23,
        "title": "2nd article",
        "user_id": 1,
        "author.username": "username_axample"
      }
    ],
  "next": true
}, status = 200
```
or if user with such id doesn't exist - see 8)

### 10. POST '/verify-token' - verify client's access-token
Body:
```
{
  "access-token" : "access.token.example"
}
```
Response:
```
{
  "username" : "some_user_name",
  "id" : 1
}, status = 200
```
