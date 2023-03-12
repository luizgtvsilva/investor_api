from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from investor_api.services import calculate_is_closed
from .models import Loan, CashFlow
from .serializers import (LoanDetailSerializer,
                          CashFlowCreateSerializer,
                          CashFlowSerializer,
                          )
from .tasks import process_csv
from django_filters.rest_framework import DjangoFilterBackend


class LoanList(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["identifier",
                        "issue_date", 
                        "total_amount", 
                        "rating", 
                        "maturity_date", 
                        "total_expected_interest_amount", 
                        "investment_date", 
                        "invested_amount", 
                        "expected_interest_amount", 
                        "is_closed", 
                        "expected_irr", 
                        "realized_irr",]

    def get(self, request):
        queryset = Loan.objects.all()
        filtered_queryset = self.filter_queryset(queryset)
        serializer = LoanDetailSerializer(filtered_queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset


class LoanDetail(APIView):
    def get_object(self, pk):
        try:
            return Loan.objects.get(pk=pk)
        except Loan.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        loan = self.get_object(pk)
        serializer = LoanDetailSerializer(loan)
        return Response(serializer.data)


class CashFlowList(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["id",
                        "reference_date", 
                        "type", 
                        "amount", 
                        "loan_identifier",]
    
    def get(self, request):
        queryset = CashFlow.objects.all()
        filtered_queryset = self.filter_queryset(queryset)
        serializer = CashFlowSerializer(filtered_queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, view=self)
        return queryset

    def post(self, request):
        serializer = CashFlowCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()

            calculate_is_closed(loan_identifier=serializer.data.get('loan_identifier'))

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CashFlowDetail(APIView):
    def get_object(self, pk):
        try:
            return CashFlow.objects.get(pk=pk)
        except CashFlow.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        cash_flow = self.get_object(pk)
        serializer = CashFlowSerializer(cash_flow)
        return Response(serializer.data)


class CsvUploadView(APIView):
    def post(self, request):
        loan_csv = request.FILES.get('loans.csv')
        cash_flow_csv = request.FILES.get('cash_flow.csv')

        if not loan_csv or not cash_flow_csv:
            return Response({'message': 'Both files is mandatory: loans.csv and cash_flow.csv'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            process_csv.delay(loan_csv.read().decode('utf-8'), cash_flow_csv.read().decode('utf-8'))
        except:
            return Response({'message': 'Was not possible start your request right now. Try again later.'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Process started.'}, status=status.HTTP_200_OK)
