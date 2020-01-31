# Simple restAPI on Flask

## Now it's little dummy, bcs I just started to learn Flask framework and REST conceptions
## NOw it uses SQlite for DB and SQlAlchemy for ORM
Ability:
1. User registration - only username and password fields, no email confirmation
2. Simple Authentification based on JWT.
3. Showing all articles, or specified article
4. Creating, Updating or Deleting article - only for registered users 

# Running locally
1. Clone && cd into repository folder
2. Create virtual environment called 'env' (bsc actually this name I'm using in .gitignore)
3. Run 'pip install -r requirements.txt'
4. Run 'db_setup.py' - creating DB
5. Run 'python app.py'
5. Open localhost:5000


# Api endpoints:

### 1. GET '/articles'  -  return list of all articles
Response:
```
  [
    {
      "id": 1,
      "text": "First post",
      "title": "Text 1"
    },
    {
      "id": 2,
      "text": "Second post",
      "title": "Text 2"
    },
  ]
```
or empty list if no articles

### 2. GET '/articles/**{id}**' - return article with specified id
Response
```
{
  "id": 1,
  "text": "Hello world, edited",
  "title": "1st articlem edited"
}
```
or if article was not found:
```
{
  "errors": "Article with id={id} not found"
}
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
	"token":"fdfdfdfd.fdfdfdfd.fdfdfdfdfdfd"
}
```
You can get valid token if login with correct username and password.
In case of invalid token you will get:
```
{
  "errors": "Invalid token"
}
```
In case of token missing:
{
  "errors": "Token is missing"
}
In case of title missing:  (for text missing - same)
```
{
  "errors": "title is missing"
}
```
### 4. PUT '/articles/edit/**{id}**' - update article with specified id & return updated article
Same as 3)
If article was not found - return respective response same as in 2)
### 5. DELETE '/articles/delete/**{id}**' - delete article with specified id & return deleted article
Headers:
```
Content-Type: application/json
```
Body:
```
{
  "token": "json.token.example"
}
```
If specified post was not found - same as 2)
### 6. POST '/register'  - register new user
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
In case of username missing (for password - the same) 
```
{'
  errors': 'username is missing'
}
```
In case when username already used:
```
{
  "errors": "User with such username already exists"
}
```
### 7. POST /login
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
  "errors": "",
  "token": "returned.token.example",
  "user_id": 1,
  "username": "username"
}
```
Or
```
{
  "errors": "Uncorrect username or password"
}
```
Or - when username is missing (for password - the same)
```
{
  "errors": "username is missing"
}
```