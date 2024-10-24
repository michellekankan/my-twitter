from testing.testcases import TestCase


class CommentModelTests(TestCase):

    def setUp(self):
        self.linghu= self.create_user('linghu')
        self.tweet = self.create_tweet(self.linghu)
        self.comment = self.create_comment(self.linghu, self.tweet)

    def test_comment(self):
        self.assertNotEqual(self.comment.__str__(), None)

    def test_like(self):
        self.create_like(self.linghu, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)
        # 針對已經按過讚的項目,第二次即使再按讚數不會變動
        self.create_like(self.linghu, self.comment)
        self.assertEqual(self.comment.like_set.count(), 1)

        dongxie = self.create_user('dongxie')
        self.create_like(dongxie, self.comment)
        self.assertEqual(self.comment.like_set.count(), 2)