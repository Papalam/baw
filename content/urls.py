from django.urls import path

from content.views import HomePageView, OurWorld, About, NewsDetail

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('our-world/', OurWorld.as_view(), name='our-world'),
    path('about/', About.as_view(), name='about'),
    path('news/<slug:slug>/', NewsDetail.as_view(), name='news_detail'),
]