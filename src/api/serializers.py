from rest_framework.serializers import (
    HyperlinkedIdentityField,
    ModelSerializer,
    SerializerMethodField,
    Serializer)

from project.models import Issue, Project, Sprint


class ProjectSerializer(ModelSerializer):
    class Meta:
        model = Project
        fields = [
            'id',
            'title',
            'description',
        ]


class IssueCreateSerializer(ModelSerializer):
    # project = ProjectSerializer()

    class Meta:
        model = Issue
        fields = [
            'title',
            'description',
            'status',
            'type',
            'estimation',
            'order',
        ]

class IssueUpdateSerializer(ModelSerializer):
    class Meta:
        model = Issue
        fields = [
            'estimation',
        ]


issue_detail_url = HyperlinkedIdentityField(
    view_name='api:detail',
)


class IssueDetailSerializer(ModelSerializer):
    # project = models.Field

    class Meta:
        model = Issue
        fields = [
            'project',
            'root',
            'title',
            'description',
            'status',
            'type',
            'estimation',
            'order',
        ]


class IssueListSerializer(ModelSerializer):
    url = issue_detail_url

    class Meta:
        model = Issue
        fields = [
            'url',
            'title',
            'description',
        ]


