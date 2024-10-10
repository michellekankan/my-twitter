from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now



class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        help_text='who posts this tweet',
    )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def hours_to_now(self):
        # created_at是有時區的 可是datetime.now()不帶時區信息, 需要增加上utc的時區信息
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        # 這裡是執行print(tweet instance)的時候會顯示的內容
        return f'{self.created_at} {self.user}: {self.content}'



from django.db import models

# Create your models here.
