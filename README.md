# Simple restAPI on Flask

## Now it's little dummy, bcs I just started to learn Flask framework and REST conceptions

# Running locally
1. Clone && cd into repository folder
2. Create virtual environment called 'env' (bsc actually this name I'm using in .gitignore)
3. Run 'pip install -r requirements.txt'
4. Run 'python app.py'
5. Open localhost:5000


# Endpoints:

### 1. GET '/articles'  -  return list of all articles
### 2. GET '/articles/**{id}**' - return article with specified id
### 3. GET '/articles/new' - create new article and return it
### 4. PUT '/articles/edit/**{id}**' - update article with specified id & return updated article
### 5. DELETE '/articles/delete/**{id}**' - delete article with specified id & return deleted article

# JSON response examples:

### List of articles:
```
[
  {
    "id": 1,
    "text": "Hello world, firstly",
    "title": "1st article"
  },
  {
    "id": 2,
    "text": "Hello world, secondly",
    "title": "2st article"
  }
]
```
### One aritcle:
```
{
    "id": 1,
    "text": "Hello world, firstly",
    "title": "1st article"
}
```

# **Testing with Postman:**
### 1., 2., 5. - Just type adress and select respective request type
### 3., 4.:
Headers:
```
content-type: application/json
```
Body (key:value pairs):
```
"title" : "title example",
"text" : "text example"
```