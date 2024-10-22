from django.contrib.contenttypes.models import ContentType
from django.test import TestCase as DjangoTestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from django.contrib.contenttypes.models import ContentType
from tweets.models import Tweet
from comments.models import Comment
from likes.models import Like




LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

# tests.py可以放在其他目錄 在執行時test時 會去找繼承TestCase的子類裡test開頭的methods
# 終端機 python manage.py test來跑測試 在跑測試時 並不會更改到實際資料庫裡的東西
class TestCase(DjangoTestCase):

    @property
    def anonymous_client(self):
        if hasattr(self, '_anoymous_client'):
            return self._anoymous_client
        self._anoymous_client = APIClient()
        return self._anoymous_client

    def create_user(self, username, email=None, password=None):
        if password is None:
            password = 'generic password'
        if email is None:
            email = f'{username}@twitter.com'
        # 不能写成 User.objects.create()
        # 因为 password 需要被加密, username 和 email 需要进行一些 normalize 处理
        return User.objects.create_user(username, email, password)

    def create_tweet(self, user, content=None):
        if content is None:
            content = 'default tweet content'
        return Tweet.objects.create(user=user, content=content)

    def create_comment(self, user, tweet, content=None):
        if content is None:
            content = 'default comment content'
        return Comment.objects.create(user=user, tweet=tweet, content=content)

    def create_like(self, user, target):
        # target is comment or tweet
        # 用get_or_create原因是同user對同target.id按多次讚只會顯示第一次 因此第一次是create之後就是get
        # 如果沒這麼寫就會違反unique_together而報錯
        # instance後面的 _ 代表的是get出來的還是create出來的, 因為我不關心這個所以我用_
        instance, _ = Like.objects.get_or_create(
            # target.__class__這個是取出target的類別是什麼 以此來說可能是Comment or Tweet
            # 找到類名還是不夠,必須要找到ContentType. 如果target是一個tweet,這裡會返回對應的ContentType實例
            content_type=ContentType.objects.get_for_model(target.__class__),
            object_id=target.id,
            user=user,
        )
        return instance
