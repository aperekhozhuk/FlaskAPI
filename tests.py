import requests
import unittest
import os


class User:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.id = None
        self.access_token = None
        self.articles = []

class Article:

    def __init__(self, title, text):
        self.title = title
        self.text = text
        self.id = None
        self.user_id = None

class Api:

    def __init__(self):
        self.root_url = "http://localhost:5000/{}"
        self.headers = {'Content-Type': 'application/json'}

    def register(self, user):
        url = self.root_url.format('register')
        response = requests.post(
            url = url,
            json = {'username' : user.username, 'password' : user.password},
            headers = self.headers
        )
        status = response.status_code
        error = ''
        if status == 200:
            user.id = response.json()['id']
        else:
            error = response.json()['error']
        return status, error

    def login(self, user):
        url = self.root_url.format('login')
        response = requests.post(
            url = url,
            json = {'username' : user.username, 'password' : user.password},
            headers = self.headers
        )
        status = response.status_code
        error = ''
        if status == 200:
            user.access_token = response.json()['access-token']
        else:
            error = response.json()['error']
        return status, error

    def create_new_article(self, user, article):
        url = self.root_url.format('articles/new')
        response = requests.post(
            url = url,
            json = {
                'title' : article.title,
                'text' : article.text,
                'access-token': user.access_token
            },
            headers = self.headers
        )
        status = response.status_code
        error = ''
        if status == 200:
            data = response.json()
            article.id = data['id']
            article.user_id = data['user_id']
            user.articles.append(article)
        else:
            error = response.json()['error']
        return status, error

    def edit_article(self, user, article):
        url = self.root_url.format('articles/{}/edit'.format(article.id))
        response = requests.put(
            url = url,
            json = {
                'title' : article.title + 'edited',
                'text' : article.text + 'edited',
                'access-token': user.access_token
            },
            headers = self.headers
        )
        return response

    def delete_article(self, user, article):
        url = self.root_url.format('articles/{}/delete'.format(article.id))
        response = requests.delete(
            url = url,
            json = {
                'access-token': user.access_token
            },
            headers = self.headers
        )
        return response

    def get_last_articles(self, user_id = None, page = 1):
        endpoint = 'articles?page={}'.format(page)
        if user_id:
            endpoint = 'users/{}/'.format(user_id) + endpoint
        url = self.root_url.format(endpoint)
        response = requests.get(url = url)
        return response

    def get_all_articles(self, user_id = None):
        endpoint = 'articles?page={}'
        if user_id:
            endpoint = 'users/{}/'.format(user_id) + endpoint
        page=1
        articles = []
        while True:
            url = self.root_url.format(endpoint.format(page))
            current_page = requests.get(url = url).json()
            if current_page:
                articles += current_page
                page += 1
            else:
                break
        return articles

    def get_article(self, id):
        url = self.root_url.format('articles/{}'.format(id))
        response = requests.get(url = url)
        return response

    def get_user_profile(self, id):
        url = self.root_url.format('users/{}'.format(id))
        response = requests.get(url = url)
        return response

    def compare_article(self, stored_article, retrieved_article, unit_test):
        unit_test.assertEqual(stored_article.id, retrieved_article['id'])
        unit_test.assertEqual(stored_article.user_id, retrieved_article['user_id'])
        unit_test.assertEqual(stored_article.title, retrieved_article['title'])

class TestApi(unittest.TestCase):

    first_user = User(username = 'user#1', password = 'Password#1')
    second_user = User(username = 'user#2', password = 'Password#1')

    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self.Api = Api()

        self.user_with_short_name = User(
            username = 'name',
            password = 'lorem_ipsum'
        )
        self.user_with_weak_pass = User(
            username = 'JohnDoe',
            password = 'weak_password'
        )
        self.user_that_repeats = self.__class__.first_user
        self.user_unregistered = User(
            username = 'UserThatDidntSignUp',
            password = 'Unregistered#1'
        )

    # Out tests execute in exactly written order,
    # because its simplify our testing process, making it more monolitic

    # During this test we also register our two users in API
    # Warning! Exectuting of this test makes changes to our local state
    def test_a1_user_can_signup(self):
        status, error = self.Api.register(self.__class__.first_user)
        self.assertEqual(status, 200)
        status, erorr = self.Api.register(self.__class__.second_user)
        self.assertEqual(status, 200)


    def test_a2_user_cant_signup_with_used_username(self):
        status, error = self.Api.register(self.__class__.first_user)
        self.assertEqual(status, 409)
        self.assertEqual(error, 'User with such name already exists')

    def test_a3_user_cant_signup_with_bad_creds(self):
        status, error = self.Api.register(self.user_with_short_name)
        self.assertEqual(status, 400)
        self.assertEqual(error, 'Bad username format')
        status, error = self.Api.register(self.user_with_weak_pass)
        self.assertEqual(status, 400)
        self.assertEqual(error, 'Bad password format')

    # After executing this test - our users get valid access-tokens.
    # We will use their in next tests
    def test_a4_user_can_login(self):
        status, error = self.Api.login(self.__class__.first_user)
        self.assertEqual(status, 200)
        status, error = self.Api.login(self.__class__.second_user)
        self.assertEqual(status, 200)

    def test_a5_unregistered_user_cant_login(self):
        status, error = self.Api.login(self.user_unregistered)
        self.assertEqual(status, 401)
        self.assertEqual(error, 'Uncorrect username or/and password')

    # During this test we are creating one article of our first_user
    def test_a6_user_can_create_article(self):
        article = Article(title = 'Title', text = 'Text')
        user = self.__class__.first_user
        status, error = self.Api.create_new_article(user, article)
        self.assertEqual(status, 200)
        self.assertEqual(article.user_id, user.id)
        # Check, that we really can retrieve this article from api
        response = self.Api.get_article(article.id)
        self.assertEqual(response.json()['id'], article.id)

    # Here we edit previously created article of first_user
    def test_a7_user_can_edit_own_article(self):
        user = self.__class__.first_user
        article = self.__class__.first_user.articles[0]
        response = self.Api.edit_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['user_id'], user.id)
        self.assertEqual(data['id'], article.id)
        self.assertEqual(data['title'], article.title + 'edited')
        self.assertEqual(data['text'], article.text + 'edited')

    def test_a8_user_cant_edit_not_own_article(self):
        user = self.__class__.second_user
        article = self.__class__.first_user.articles[0]
        response = self.Api.edit_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], 'You can edit only own article')

    def test_a9_user_cant_delete_not_own_article(self):
        user = self.__class__.second_user
        article = self.__class__.first_user.articles[0]
        response = self.Api.delete_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 403)
        self.assertEqual(data['error'], 'You can delete only own article')

    def test_b1_user_without_token_cant_edit(self):
        user = self.user_unregistered
        article = self.__class__.first_user.articles[0]
        response = self.Api.edit_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Access-token is missing. Log in, please')

    def test_b2_user_without_token_cant_delete(self):
        user = self.user_unregistered
        article = self.__class__.first_user.articles[0]
        response = self.Api.delete_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Access-token is missing. Log in, please')

    def test_b3_user_with_ivalid__token_cant_edit(self):
        user = self.user_unregistered
        user.access_token = self.__class__.first_user.access_token[1:]
        article = self.__class__.first_user.articles[0]
        response = self.Api.edit_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Invalid access-token. Log in please')

    def test_b4_user_with_invalid_token_cant_delete(self):
        user = self.user_unregistered
        user.access_token = self.__class__.first_user.access_token[1:]
        article = self.__class__.first_user.articles[0]
        response = self.Api.delete_article(user, article)
        data = response.json()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(data['error'], 'Invalid access-token. Log in please')

    # And finally we delete first_user's article from API
    # And we delete it from our local state (better for future tests)
    def test_b5_user_can_delete_own_article(self):
        user = self.__class__.first_user
        article = self.__class__.first_user.articles[0]
        response = self.Api.delete_article(user, article)
        data = response.json()
        user.articles = []
        self.assertEqual(response.status_code, 200)

    def test_b5_user_with_invalid_token_cant_create(self):
        article = Article(title = 'Title', text = 'Text')
        user = self.user_unregistered
        status, error = self.Api.create_new_article(user, article)
        self.assertEqual(status, 401)
        self.assertEqual(error, 'Access-token is missing. Log in, please')

    # Please, note, that during previous tests:
    # first_user created one article, then edited it, and, finally,
    # deleted it. So for now we shouldn't see any articles
    def test_b6_no_articles_present(self):
        response = self.Api.get_last_articles()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    # During our tests we registered two users (and only two),
    # so we can get their profiles by their ID's.
    # Also we can't get profile by ID that is missing.
    # For example, we can take thaa ID as sum of ID's of two existing users
    def test_b7_get_user_profile(self):
        first_user = self.__class__.first_user
        second_user = self.__class__.second_user
        missed_user_id = first_user.id + second_user.id
        response1 = self.Api.get_user_profile(first_user.id)
        response2 = self.Api.get_user_profile(second_user.id)
        response3 = self.Api.get_user_profile(missed_user_id)
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(response3.status_code, 404)
        self.assertEqual(response1.json()['username'], first_user.username )
        self.assertEqual(response2.json()['username'], second_user.username )
        self.assertEqual(response3.json()['error'],
            'User with id={} was not found'.format(missed_user_id)
        )

    # In that test we create bunch of articles (15 for each of our two users)
    # And after that checking that we really can retrieve all
    # of this articles from API
    def test_b8_test_create_many_articles(self):
        article_count = 15
        first_user = self.__class__.first_user
        second_user = self.__class__.second_user
        for i in range(1, article_count + 1):
            title1 = 'Title {} | {}'.format(i, 1)
            text1 = 'Text {} | {}'.format(i, 1)
            article1 = Article(title = title1, text = text1)
            title2 = 'Title {} | {}'.format(i, 2)
            text2 = 'Text {} | {}'.format(i, 2)
            article2 = Article(title = title2, text = text2)
            self.Api.create_new_article(first_user, article1)
            self.Api.create_new_article(second_user, article2)
        # Here we will store articles, actually getted from API
        first_user_articles = self.Api.get_all_articles(
            user_id = first_user.id
        )
        second_user_articles = self.Api.get_all_articles(
            user_id = second_user.id
        )
        # Here we have articles, that we tried to create
        first_user_articles_local = first_user.articles
        second_user_articles_local = second_user.articles
        # Checking - if all articles that we tried to create
        # was really added to API
        # Firstly, lets check only by count
        self.assertEqual(
            len(first_user_articles), len(first_user_articles_local)
        )
        self.assertEqual(
            len(first_user_articles), len(first_user_articles_local)
        )
        for i in range(article_count):
            retrieved_article = first_user_articles[i]
            stored_article = first_user.articles[article_count - 1 - i]
            self.Api.compare_article(stored_article, retrieved_article, self)
        all_articles = self.Api.get_all_articles()
        # Check, if total count of articles matches with
        # sum of counts of articles of both users
        self.assertEqual(len(all_articles), 2 * article_count)


if __name__ == '__main__':
    print('Creating temporarry Database')
    # Actually, we just hide our db and create new one
    # And after that we delete tempoprary db and return our old one
    try:
        os.rename('db.sqlite', 'db.sqlite.backup')
    except:
        pass
    os.system('flask db upgrade')
    try:
        unittest.main()
    except:
        pass
    print('Removing temporary Database')
    os.remove('db.sqlite')
    try:
        os.rename('db.sqlite.backup', 'db.sqlite')
    except:
        pass
