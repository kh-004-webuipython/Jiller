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


class IssueCreateUpdateSerializer(ModelSerializer):
    # project = ProjectSerializer()

    class Meta:
        model = Issue
        fields = [
            'root',
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

    class Meta:
        model = Issue
        fields = [
            'url',
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

    # user = UserDetailSerializer(read_only=True)

    class Meta:
        model = Issue
        fields = [
            'url',
            'title',
            'description',
        ]


class IssueCustomSerializer(Serializer):
    def get_issue(self, issue):
        mapped_object = {
            'project': issue.project.id,
            'root': issue.root,
            'title': issue.title,
            'description': issue.description,
            'status': issue.status,
            'type': issue.type,
            'order': issue.order,
        }

        return mapped_object
