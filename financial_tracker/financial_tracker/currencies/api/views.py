from ..models import Currency, ExchangeRate
from rest_framework import viewsets
from .serializers import CurrencySerializer, ExchangeRateSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from rest_framework import status
import logging

logger = logging.getLogger(__name__)
# Create your views here.

class CurrencyViewSet(viewsets.ModelViewSet):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_local']  # Enable filtering by `is_local`
    #lookup_field = 'code'  # Use the `code` field as the lookup field

    def perform_create(self, serializer):
        try:
            serializer.save(created_by=self.request.user)
        except IntegrityError:
            raise APIException("Only one local currency can exist.")  # Use DRF's APIException for a unified response
        except ValidationError as e:
            raise APIException(e.message_dict if hasattr(e, "message_dict") else str(e))

    def perform_update(self, serializer):
        try:
            serializer.save(modified_by=self.request.user)
        except IntegrityError:
            raise APIException("Only one local currency can exist.")
        except ValidationError as e:
            raise APIException(e.message_dict if hasattr(e, "message_dict") else str(e))

class ExchangeRateViewSet(viewsets.ModelViewSet):
    queryset = ExchangeRate.objects.all()
    serializer_class = ExchangeRateSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['currency']  # Enable filtering by `currency`

    # def perform_create(self, serializer):
    #     # Check if the currency is local before saving
    #     currency = serializer.validated_data.get('currency')
    #     if currency.is_local:
    #         raise ValidationError("Exchange rates cannot be assigned to local currencies.")
    #     serializer.save(created_by=self.request.user)
    
    def perform_create(self, serializer):
        currency = serializer.validated_data.get('currency')
        if currency.is_local:
            raise ValidationError({"non_field_errors": ["Exchange rates cannot be assigned to local currencies."]})
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        # Check if the currency is local before updating
        currency = serializer.validated_data.get('currency')
        if currency.is_local:
            raise ValidationError("Exchange rates cannot be assigned to local currencies.")
        serializer.save(modified_by=self.request.user)

class GetLocalCurrencyAPIView(APIView):
    def get(self, request):
        try:
            local_currency = Currency.objects.get(is_local=True)
            local_currency_code = local_currency.code
            return Response({"local_currency_code": local_currency_code})
        except Currency.DoesNotExist:
            #error_message = "No local currency is set in the system."
            #logger.error(f"GetLocalCurrencyAPIView: {error_message}")
            return Response({"error": "No local currency is set in the system."}, status=404)
        except Exception as e:
            logger.exception("Unexpected error in GetLocalCurrencyAPIView")
            return Response({"error": "An unexpected error occurred."}, status=500)