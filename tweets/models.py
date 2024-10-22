from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from utils.time_helpers import utc_now
from likes.models import Like

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # user 及 created_at的聯合索引(compound/composite)
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')  #再次編輯model時要在執行makemigrations及migrate

    @property
    def hours_to_now(self):
        # created_at是有時區的 可是datetime.now()不帶時區信息, 需要增加上utc的時區信息
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def like_set(self): #self代表的是當前的實例
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        # 這裡是執行print(tweet instance)的時候會顯示的內容
        return f'{self.created_at} {self.user}: {self.content}'

