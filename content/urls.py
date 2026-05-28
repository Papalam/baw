from django.urls import path

from content.views import HomePageView, OurWorld, About, NewsArticleListView, NewsArticleDetailView, BuyersView, \
    StoriesListView, ContactFormView, TestDriveView, CompletionComparisonView, SpecialOfferView, CorporateClientsView, \
    NearestDealerView, PrivacyPolicyView

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('our-world/', OurWorld.as_view(), name='our-world'),
    path('about/', About.as_view(), name='about'),
    path('news/', NewsArticleListView.as_view(), name='news-list'),
    path('news/<slug:slug>/', NewsArticleDetailView.as_view(), name='news-detail'),
    path('buyers/', BuyersView.as_view(), name='buyers'),
    path('stories/', StoriesListView.as_view(), name='stories'),
    path('callback/', ContactFormView.as_view(), name='callback'),
    path('test-drive/', TestDriveView.as_view(), name='test-drive'),
    path('trim-levels/', CompletionComparisonView.as_view(), name='trim-levels'),
    path('offers/', SpecialOfferView.as_view(), name='offers'),
    path('corporate/', CorporateClientsView.as_view(), name='corporate'),
    path('nearest-dealer/', NearestDealerView.as_view(), name='nearest_dealer'),
    path('privacy-policy/', PrivacyPolicyView.as_view(), name='privacy-policy'),
]
