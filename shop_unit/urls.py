from django.urls import path
from shop_unit import views

urlpatterns = [
	path('imports', views.imports, name='imports'),
	path('delete/<uuid>', views.delete, name='delete'),
	path('nodes/<uuid>', views.nodes, name='nodes'),
]