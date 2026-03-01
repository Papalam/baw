from django.urls import path

from content.views import HomePageView, OurWorld

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('our-world/', OurWorld.as_view(), name='our-world'),
]