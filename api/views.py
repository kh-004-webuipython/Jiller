from django.db.models import Q


from rest_framework.filters import (
        SearchFilter,
        OrderingFilter,
    )
from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    ListAPIView,
    UpdateAPIView,
    RetrieveAPIView,
    RetrieveUpdateAPIView
    )



from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
    IsAdminUser,
    IsAuthenticatedOrReadOnly,

    )

from project.models import Issue

# from .pagination import PostLimitOffsetPagination, PostPageNumberPagination
# from .permissions import IsOwnerOrReadOnly

from .serializers import (
    IssueCreateUpdateSerializer,
    IssueDetailSerializer,
    IssueListSerializer
    )


class IssueCreateAPIView(CreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueCreateUpdateSerializer
    #permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IssueDetailAPIView(RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueDetailSerializer
    # lookup_field = 'slug'
    # permission_classes = [AllowAny]
    #lookup_url_kwarg = "abc"


class IssueUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueCreateUpdateSerializer
    # lookup_field = 'slug'
    # permission_classes = [IsOwnerOrReadOnly]
    #lookup_url_kwarg = "abc"
    def perform_update(self, serializer):
        serializer.save(user=self.request.user)
        #email send_email



# class IssueDeleteAPIView(DestroyAPIView):
#     queryset = Issue.objects.all()
#     serializer_class = PostDetailSerializer
#     lookup_field = 'slug'
#     permission_classes = [IsOwnerOrReadOnly]
#     #lookup_url_kwarg = "abc"


class IssueListAPIView(ListAPIView):
    serializer_class = IssueListSerializer
    filter_backends= [SearchFilter, OrderingFilter]
    # permission_classes = [AllowAny]
    # search_fields = ['title', 'content', 'user__first_name']
    # pagination_class = PostPageNumberPagination #PageNumberPagination

    def get_queryset(self, *args, **kwargs):
        #queryset_list = super(PostListAPIView, self).get_queryset(*args, **kwargs)
        queryset_list = Issue.objects.all().filter(status=Issue.NEW)
        # query = self.request.GET.get("q")
        # if query:
        #     queryset_list = queryset_list.filter(
        #             Q(title__icontains=query)|
        #             Q(content__icontains=query)|
        #             Q(user__first_name__icontains=query) |
        #             Q(user__last_name__icontains=query)
        #             ).distinct()
        return queryset_list













