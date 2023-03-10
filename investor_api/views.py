from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Loan, CashFlow
from .serializers import (LoanDetailSerializer,
                          LoanCreateSerializer,
                          CashFlowCreateSerializer,
                          CashFlowSerializer,
                          )


class LoanList(APIView):
    def get(self, request):
        loans = Loan.objects.all()
        serializer = LoanDetailSerializer(loans, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = LoanCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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

    def put(self, request, pk):
        loan = self.get_object(pk)
        serializer = LoanCreateSerializer(loan, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        loan = self.get_object(pk)
        loan.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CashFlowList(APIView):
    def get(self, request):
        cash_flows = CashFlow.objects.all()
        serializer = CashFlowSerializer(cash_flows, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CashFlowCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
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

    def put(self, request, pk):
        cash_flow = self.get_object(pk)
        serializer = CashFlowCreateSerializer(cash_flow, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        cash_flow = self.get_object(pk)
        cash_flow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)