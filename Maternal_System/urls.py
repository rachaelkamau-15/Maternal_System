from django.contrib import admin
from django.urls import path, include

from patients import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('patients.urls')),
    # Keep this only if you are sure appointments app works, otherwise comment it out:
    # The main payments page
]