from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from investor_api.services import calculate_is_closed
from .models import Loan, CashFlow
from .serializers import (
    LoanDetailSerializer,
    CashFlowCreateSerializer,
    CashFlowSerializer,
)
from .tasks import process_csv
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, F, FloatField, ExpressionWrapper
from django.views.generic import TemplateView
from django.views.decorators.cache import cache_page
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io
import base64
from django.utils.decorators import method_decorator


class LoanList(APIView):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        "identifier",
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
        "realized_irr",
    ]

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
    filterset_fields = [
        "id",
        "reference_date",
        "type",
        "amount",
        "loan_identifier",
    ]

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

            calculate_is_closed(loan_identifier=serializer.data.get("loan_identifier"))

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
        loan_csv = request.FILES.get("loans.csv")
        cash_flow_csv = request.FILES.get("cash_flow.csv")

        if not loan_csv or not cash_flow_csv:
            return Response(
                {"message": "Both files is mandatory: loans.csv and cash_flow.csv"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            process_csv.delay(
                loan_csv.read().decode("utf-8"), cash_flow_csv.read().decode("utf-8")
            )
        except:
            return Response(
                {
                    "message": "Was not possible start your request right now. Try again later."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response({"message": "Process started."}, status=status.HTTP_200_OK)


class InvestmentStatisticsView(APIView):

    @method_decorator(cache_page(60 * 15))
    def get(self, request):
        try:
            loans = Loan.objects.all()
            number_of_loans = len(loans)
            total_invested_amount = (
                loans.aggregate(Sum("invested_amount"))["invested_amount__sum"] or 0
            )
            current_invested_amount = (
                loans.filter(is_closed=False).aggregate(Sum("invested_amount"))[
                    "invested_amount__sum"
                ]
                or 0
            )
            total_repaid_amount = (
                CashFlow.objects.filter(type="Repayment").aggregate(Sum("amount"))[
                    "amount__sum"
                ]
                or 0
            )
            weighted_realized_irr = ExpressionWrapper(
                F("invested_amount") * F("realized_irr"), output_field=FloatField()
            )
            average_realized_irr = (
                loans.filter(is_closed=True)
                .annotate(weighted_irr=weighted_realized_irr)
                .aggregate(irr=Sum("weighted_irr") / Sum("invested_amount"))["irr"]
                or 0
            )

            response_data = {
                "number_of_loans": number_of_loans,
                "total_invested_amount": total_invested_amount,
                "current_invested_amount": current_invested_amount,
                "total_repaid_amount": total_repaid_amount,
                "average_realized_irr": average_realized_irr,
            }

            return Response(response_data)
        except:
            return Response(
                {"message": "Was not possible return the investment informations."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class InvestmentStatisticsTemplateView(TemplateView):
    template_name = "investment_statistics.html"

    @method_decorator(cache_page(60 * 15))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        loans = Loan.objects.all()
        total_invested_amount = (
            loans.aggregate(Sum("invested_amount"))["invested_amount__sum"] or 0
        )
        context["total_invested_amount"] = total_invested_amount
        context["num_loans"] = len(loans)
        context["current_invested_amount"] = (
            loans.filter(is_closed=False).aggregate(Sum("invested_amount"))[
                "invested_amount__sum"
            ]
            or 0
        )
        context["total_repaid_amount"] = (
            CashFlow.objects.filter(type="Repayment").aggregate(Sum("amount"))[
                "amount__sum"
            ]
            or 0
        )
        weighted_realized_irr = ExpressionWrapper(
            F("invested_amount") * F("realized_irr"), output_field=FloatField()
        )
        context["average_realized_irr"] = (
            loans.filter(is_closed=True)
            .annotate(weighted_irr=weighted_realized_irr)
            .aggregate(irr=Sum("weighted_irr") / Sum("invested_amount"))["irr"]
            or 0
        )

        investment_distribution = []
        labels = []
        for loan in loans:
            if loan.invested_amount:
                investment_distribution.append(loan.invested_amount)
                labels.append(loan.identifier)
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        ax.pie(investment_distribution, labels=labels)
        ax.set_title("Investment Distribution")
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        context[
            "investment_distribution"
        ] = "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("utf-8")

        investment_amounts = []
        repayment_amounts = []
        labels = []
        for loan in loans:
            if loan.invested_amount:
                investment_amounts.append(-abs(loan.invested_amount))
                repayment_amounts.append(
                    CashFlow.objects.filter(
                        type="Repayment", loan_identifier=loan.identifier
                    ).aggregate(Sum("amount"))["amount__sum"]
                    or 0
                )
                labels.append(loan.identifier)
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        ax.bar(labels, investment_amounts, label="Investment")
        ax.bar(labels, repayment_amounts, label="Repayment")
        ax.set_title("Investment and Repayment by Loan")
        ax.set_xlabel("Loan Identifier")
        ax.set_ylabel("Amount")
        ax.legend()
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        context["investment_repayment"] = "data:image/png;base64," + base64.b64encode(
            buf.getvalue()
        ).decode("utf-8")

        cash_flows = CashFlow.objects.all().order_by("reference_date")
        investment_total = 0
        repayment_total = 0
        investment_data = []
        repayment_data = []
        date_labels = []
        for cash_flow in cash_flows:
            if cash_flow.type == "Funding":
                investment_total += cash_flow.amount
            else:
                repayment_total += cash_flow.amount
            investment_data.append(abs(investment_total))
            repayment_data.append(repayment_total)
            date_labels.append(cash_flow.reference_date.strftime("%Y-%m-%d"))
        fig = Figure(figsize=(6, 6))
        ax = fig.add_subplot(111)
        ax.plot(date_labels, investment_data, label="Investment")
        ax.plot(date_labels, repayment_data, label="Repayment")
        ax.set_title("Investment and Repayment over Time")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount")
        ax.legend()
        canvas = FigureCanvas(fig)
        buf = io.BytesIO()
        canvas.print_png(buf)
        context["investment_over_time"] = "data:image/png;base64," + base64.b64encode(
            buf.getvalue()
        ).decode("utf-8")
        return context