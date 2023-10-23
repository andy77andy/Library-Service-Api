from rest_framework import viewsets

from book.models import Book
from book.serializers import BookSerializer
from permissions import IsAdminOrReadOnly


class BookViewSet(
    viewsets.ModelViewSet,
):
    queryset = Book.objects.all()

    permission_classes = (IsAdminOrReadOnly,)
    serializer_class = BookSerializer
