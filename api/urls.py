from django.urls import include, path

from api.spectacular.urls import urlpatterns as doc_urls
from users.urls import drf_urlpatterns as user_urls
from blog.urls import drf_urlpatterns as blog_urls
from rating.urls import drf_urlpatterns as rating_urls
from subscription.urls import drf_urlpatterns as subscriptions_urls

app_name = 'api'
urlpatterns = [path(r'auth/', include('djoser.urls.jwt')),]

urlpatterns += doc_urls
urlpatterns += user_urls
urlpatterns += blog_urls
urlpatterns += rating_urls
urlpatterns += subscriptions_urls
