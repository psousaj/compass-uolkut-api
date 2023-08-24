from django.urls import path

from user.views import ProfileView, UserView

urlpatterns = [
    path("", ProfileView.as_view({"get": "list"})),
    path("/update", ProfileView.as_view({"patch": "patch"})),
    path("/signup", ProfileView.as_view({"post": "create"})),
    path("/users", UserView.as_view()),
]
