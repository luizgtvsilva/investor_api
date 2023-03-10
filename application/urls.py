"""application URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from investor_api.views import (LoanList,
                                LoanDetail,
                                CashFlowList,
                                CashFlowDetail,
                                )


urlpatterns = [
    path('admin/', admin.site.urls),
    path('loans/', LoanList.as_view()),
    path('loans/<int:pk>/', LoanDetail.as_view()),
    path('cashflows/', CashFlowList.as_view()),
    path('cashflows/<int:pk>/', CashFlowDetail.as_view()),
]
