from rest_framework import viewsets, filters, status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from ..models import EarnedIncome, PortfolioIncome, PassiveIncome
from . serializers import EarnedIncomeSerializer, PortfolioIncomeSerializer, PassiveIncomeSerializer
from rest_framework.views import APIView
from django.db.models import Sum
from rest_framework.response import Response

# Create your views here.
class EarnedIncomeViewSet(viewsets.ModelViewSet):
    queryset = EarnedIncome.objects.all()
    serializer_class = EarnedIncomeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['income_name', 'currency__symbol']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

class PortfolioIncomeViewSet(viewsets.ModelViewSet):
    queryset = PortfolioIncome.objects.all()
    serializer_class = PortfolioIncomeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['income_name', 'currency__symbol']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

class PassiveIncomeViewSet(viewsets.ModelViewSet):
    queryset = PassiveIncome.objects.all()
    serializer_class = PassiveIncomeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['income_name', 'currency__symbol']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    def perform_update(self, serializer):
        serializer.save(modified_by=self.request.user)

class TotalIncomeAPIView(APIView):
    
    def calculate_total_income(self):
                # Annotate the total sum of 'amount' for each queryset
        earned_income_queryset = EarnedIncome.objects.annotate(total_amount=Sum('amount'))
        portfolio_income_queryset = PortfolioIncome.objects.annotate(total_amount=Sum('amount'))
        passive_income_queryset = PassiveIncome.objects.annotate(total_amount=Sum('amount'))

        # Sum the 'total_amount' from all the querysets
        earned_income_total = earned_income_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        portfolio_income_total = portfolio_income_queryset.aggregate(total=Sum('total_amount'))['total'] or 0
        passive_income_total = passive_income_queryset.aggregate(total=Sum('total_amount'))['total'] or 0

        # Calculate the total income
        total_income = earned_income_total + portfolio_income_total + passive_income_total
        return total_income

    def get(self, request):
        total_income = self.calculate_total_income()
        return Response({"total_income": total_income}, status=status.HTTP_200_OK)