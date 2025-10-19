"""Module imports for viewsets"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter

from django_filters.rest_framework import DjangoFilterBackend
from .models import Property, Booking, Review, User
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    BookingListSerializer,
    BookingDetailSerializer,
    ReviewSerializer,
    UserSerializer,
)


class PropertyViewSet(viewsets.ModelViewSet):
    queryset = Property.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["host", "location"]
    search_fields = ["name", "description", "location"]
    ordering_fields = ["pricepernight", "created_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "list":
            return PropertyListSerializer
        return PropertyDetailSerializer

    @action(detail=True, methods=["get"])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific property"""
        property_obj = self.get_object()
        bookings = property_obj.bookings.all()
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific property"""
        property_obj = self.get_object()
        reviews = property_obj.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["property_obj", "user", "status"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == "list":
            return BookingListSerializer
        return BookingDetailSerializer

    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        """Confirm a pending booking"""
        booking = self.get_object()
        if booking.status != "pending":
            return Response(
                {"error": "Only pending bookings can be confirmed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = "confirmed"
        booking.save()
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a booking"""
        booking = self.get_object()
        if booking.status == "canceled":
            return Response(
                {"error": "Booking is already canceled."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = "canceled"
        booking.save()
        serializer = BookingDetailSerializer(booking)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Review model providing CRUD operations.
    """

    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ["listing_id", "user", "rating"]
    ordering_fields = ["rating", "created_at"]
    ordering = ["-created_at"]


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User model providing CRUD operations.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ["role"]
    search_fields = ["first_name", "last_name", "email"]
    ordering_fields = ["first_name", "last_name", "created_at"]
    ordering = ["-created_at"]

    @action(detail=True, methods=["get"])
    def properties(self, request, pk=None):
        """Get all properties for a specific host"""
        user = self.get_object()
        if user.role not in ["host", "admin"]:
            return Response(
                {"error": "User is not a host or admin."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        properties = user.properties.all()
        serializer = PropertyListSerializer(properties, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def bookings(self, request, pk=None):
        """Get all bookings for a specific user"""
        user = self.get_object()
        bookings = user.bookings.all()
        serializer = BookingListSerializer(bookings, many=True)
        return Response(serializer.data)