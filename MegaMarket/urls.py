from django.urls import path, include

urlpatterns = [
	path('', include('shop_unit.urls')),
]
