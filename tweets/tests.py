from datetime import timedelta
from utils.time_helpers import utc_now
from testing.testcases import TestCase


class TweetTests(TestCase):

    def setUp(self):
        self.linghu = self.create_user('lingu')
        self.tweet = self.create_tweet(self.linghu, content='Jiuzhang Dafa Good!')

    def test_hours_to_now(self):
        self.tweet.created_at = utc_now() - timedelta(hours=10)
        self.tweet.save()
        self.assertEqual(self.tweet.hours_to_now, 10)

    def test_like(self):
        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)
        # 針對已經按過讚的項目,第二次即使再按讚數不會變動
        self.create_like(self.linghu, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.tweet)
        self.assertEqual(self.tweet.like_set.count(), 2)
