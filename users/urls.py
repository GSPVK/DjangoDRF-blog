from django.urls import path
from users.views import users
from users.api.views import users as users_api


app_name = 'users'
urlpatterns = [
    path('signup/', users.SignUpView.as_view(), name='signup'),
    path('profile/<int:pk>/', users.UserProfileView.as_view(), name='profile'),
    path('<int:pk>/edit/', users.UserProfileEditView.as_view(), name='profile-edit'),
]

drf_urlpatterns = [
    path('signup/', users_api.SignUpAPIView.as_view(), name='signup'),
    path('change-password/', users_api.ChangePasswordAPIView.as_view(), name='change-password'),
    path('me/', users_api.MeAPIView.as_view(), name='me'),
    path('me/full/', users_api.FullMeAPIView.as_view(), name='me-full'),
    path('users/<int:pk>/', users_api.UserProfileAPIView.as_view(), name='user-profile'),
    path('users/<int:pk>/full/', users_api.FullUserProfileAPIView.as_view(), name='user-profile-full'),
]
