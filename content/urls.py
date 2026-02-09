from django.urls import path

from content.views import HomePageView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
]