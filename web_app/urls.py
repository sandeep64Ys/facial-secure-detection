from django.contrib import admin
from django.urls import path 
from .views import *
urlpatterns = [
    path('home/',home),
    path('cat/',category_d),
    path('emp/',employee_d),
    path('cust/',customer_d),
    path('service/',service_d),
    path('attend/',attendence_d),
    path('cat_view/',cat_view),
    path('emp_view/',emp_view),
    path('cust_view/',cust_view),
    path('serv_view/',serv_view),
    path('attend_view/',attend_view),
    path("video_feed/", video_feed, name="video_feed"),
    path("video_feed_out/", video_feed_out, name="video_feed"),
    path("salary/", salary_view, name="salary"),
    path('export-salary/', export_salary_report, name='export_salary'),
    path('salary_chart/',salary_chart, name='salary_chart'),
]