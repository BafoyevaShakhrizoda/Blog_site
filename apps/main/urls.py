from django.urls import path
from .views import HomeView

app_name = 'main'

urlpatterns = [
    # path('', IndexView.as_view(), name='index'),

    path("", HomeView.as_view(), name="home"),

]



