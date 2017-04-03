from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

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
    IssueDetailSerializer,
    IssueListSerializer,
    IssueCreateSerializer, IssueUpdateSerializer)


class IssueCreateAPIView(CreateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueCreateSerializer

    # def perform_create(self, serializer):
    #     serializer.save(user=self.request.user)


class IssueDetailAPIView(RetrieveAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueDetailSerializer


class IssueUpdateAPIView(RetrieveUpdateAPIView):
    queryset = Issue.objects.all()
    serializer_class = IssueUpdateSerializer


class IssueListAPIView(ListAPIView):
    serializer_class = IssueListSerializer
    filter_backends = [SearchFilter, OrderingFilter]

    def get_queryset(self, *args, **kwargs):
        queryset_list = Issue.objects.all()
        return queryset_list
