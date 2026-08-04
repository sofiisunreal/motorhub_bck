from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notice
from .serializers import NoticeSerializer
from rest_framework.decorators import action


class NoticeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        notices = Notice.objects.filter(
            is_archived=False
        ).order_by("-created_at")

        serializer = NoticeSerializer(notices, many=True)
        return Response(serializer.data)
    # GET /api/notices/1/
    def retrieve(self, request, pk=None):
        try:
            notice = Notice.objects.get(id=pk)
        except Notice.DoesNotExist:
            return Response(
                {"error": "Notice not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NoticeSerializer(notice)
        return Response(serializer.data)

    # POST /api/notices/
    def create(self, request):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can create notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = NoticeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(posted_by=request.user)
            return Response(
                {
                    "message": "Notice created successfully.",
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # PATCH /api/notices/1/
    def partial_update(self, request, pk=None):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can update notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            notice = Notice.objects.get(id=pk)
        except Notice.DoesNotExist:
            return Response(
                {"error": "Notice not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = NoticeSerializer(
            notice,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Notice updated successfully.",
                    "data": serializer.data
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE /api/notices/1/
    def destroy(self, request, pk=None):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can delete notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            notice = Notice.objects.get(id=pk)
        except Notice.DoesNotExist:
            return Response(
                {"error": "Notice not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        notice.delete()

        return Response(
            {"message": "Notice deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )
    # PATCH /api/notices/1/archive/
    @action(detail=True, methods=["patch"])
    def archive(self, request, pk=None):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can archive notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            notice = Notice.objects.get(id=pk)

        except Notice.DoesNotExist:
            return Response(
                {"error": "Notice not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        notice.is_archived = True
        notice.save()

        return Response(
            {"message": "Notice archived successfully."},
            status=status.HTTP_200_OK
        )
    # GET /api/notices/archived/
    @action(detail=False, methods=["get"])
    def archived(self, request):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can view archived notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        notices = Notice.objects.filter(
            is_archived=True
        ).order_by("-created_at")

        serializer = NoticeSerializer(
            notices,
            many=True
        )

        return Response(serializer.data)

    # PATCH /api/notices/1/restore/
    @action(detail=True, methods=["patch"])
    def restore(self, request, pk=None):

        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can restore notices."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            notice = Notice.objects.get(id=pk)

        except Notice.DoesNotExist:
            return Response(
                {"error": "Notice not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        notice.is_archived = False
        notice.save()

        return Response(
            {"message": "Notice restored successfully."}
        )
