from django.urls import path

from content.views import HomePageView, OurWorld, About, NewsArticleListView, NewsArticleDetailView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('our-world/', OurWorld.as_view(), name='our-world'),
    path('about/', About.as_view(), name='about'),
    path('news/', NewsArticleListView.as_view(), name='news-list'),
    path('news/<slug:slug>/', NewsArticleDetailView.as_view(), name='news-detail'),
]