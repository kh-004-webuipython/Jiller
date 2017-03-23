from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField
)
#
# from accounts.api.serializers import UserDetailSerializer
# from comments.api.serializers import CommentSerializer
# from comments.models import Comment

from project.models import Issue, Project, Sprint


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = [
            # 'id',
            'title',
            'description',
        ]


class IssueCreateUpdateSerializer(ModelSerializer):
    # project = ProjectSerializer()

    class Meta:
        model = Issue
        fields = [
            # 'id',
            'root',
            # 'project',
            'title',
            'description',
            'status',
            'type',
            'estimation',
            'order',
        ]


issue_detail_url = HyperlinkedIdentityField(
    view_name='api:detail',
)


class IssueDetailSerializer(ModelSerializer):
    url = issue_detail_url

    # user = UserDetailSerializer(read_only=True)
    # image = SerializerMethodField()
    # html = SerializerMethodField()
    # comments = SerializerMethodField()

    class Meta:
        model = Issue
        fields = [
            'url',
            'project',
            'sprint',
            'root',
            'title',
            'description',
            'status',
            'type',
            'estimation',
            'order',
        ]

        # def get_html(self, obj):
        #     return obj.get_markdown()
        #
        # def get_image(self, obj):
        #     try:
        #         image = obj.image.url
        #     except:
        #         image = None
        #     return image
        #
        # def get_comments(self, obj):
        #     c_qs = Comment.objects.filter_by_instance(obj)
        #     comments = CommentSerializer(c_qs, many=True).data
        #     return comments


class IssueListSerializer(ModelSerializer):
    url = issue_detail_url

    # user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = [
            'url',
            'title',
            'description',
        ]
