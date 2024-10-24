from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner
from inbox.services import NotificationService
from utils.decorators import required_params


class CommentViewSet(viewsets.GenericViewSet):

    #只实现 list, create, update, destroy 的方法
    #不实现 retrieve（查询单个 comment） 的方法，因为没这个需求

    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # detail = False
    # POST /api/comments/ -> create
    # GET /api/comments/?tweet_id=1 -> list
    # detail = True
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        # 注意要加用 AllowAny() / IsAuthenticated() 实例化出对象
        # 而不是 AllowAny / IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            # 這個放list原因是因為會先檢測是否登入 如果fail就不會檢查下一個了
            # 如果obj不是當前用戶 那會返回message = "You do not have permission to access this object"
            # 所以假設只放IsObjectOwner()雖然也是會運作 但如果你是因為沒登入而返回上述訊息 就會被誤導
            # 因為應該是你沒登入而非你不是當前用戶
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self, request, *args, **kwargs):
        # 不做任何權限檢測
        # if 'tweet_id' not in request.query_params:
        #     return Response(
        #         {
        #             'message': 'missing tweet_id in request',
        #             'success': False,
        #         },
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        # 使用filterset_fields()前
        # tweet_id = request.query_params['tweet_id']
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        queryset = self.get_queryset()
        # 加.prefetch_related是為了從數據庫優化增加查詢效率 發現留言只有一個user 所以到User的數據庫裡就找一次user的資料就好了(不管這個user總共留多少個言)
        comments = self.filter_queryset(queryset).prefetch_related('user').order_by('created_at')
        serializer = CommentSerializer(
            comments,
            context={'request':request},
            many=True,
        )
        # many = True代表返回的JSON是一個list
        return Response({'comments':serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # 注意这里必须要加 'data=' 来指定参数是传给 data 的
        # 因为默认的第一个参数是 instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save 方法会触发 serializer 里的 create 方法，点进 save 的具体实现里可以看到
        comment = serializer.save()
        NotificationService.send_comment_notification(comment)
        return Response(
            CommentSerializer(comment, context={'request':request}).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object 是 DRF 包装的一个函数，会在找不到的时候 raise 404 error
        # 所以这里无需做额外判断
        # get_object()拿到的就是url裡的id, 再拿以上queryset去filter id = url的id 並拿到url id的comment
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)
        # save 方法会触发 serializer 里的 update 方法，点进 save 的具体实现里可以看到
        # save 是根据 instance 参数有没有传来决定是触发 create 还是 update
        comment = serializer.save()
        return Response(
            CommentSerializer(comment, context={'request':request}).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF 里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        return Response({'success': True}, status=status.HTTP_200_OK)