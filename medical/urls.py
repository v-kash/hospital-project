from django.urls import path
from . import views

urlpatterns = [
    path('doctors/', views.DoctorListView.as_view(), name='doctor-list-create'),
    path('doctors/<int:pk>/', views.doctor_detail, name='doctor-detail'),
    path('patients/', views.PatientListView.as_view(), name='patient-list-create'),
    path('patients/<int:pk>/', views.patient_detail, name='patient-detail'),
    path('patient_records/', views.PatientRecordListCreateView.as_view(), name='patient-record-list-create'),
    path('patient_records/<int:pk>/', views.patient_record_detail, name='patient-record-detail'),
    path('departments/', views.DepartmentListView.as_view(), name='department-list-create'),
    path('department/<int:pk>/doctors/', views.DepartmentDoctorsListView.as_view(), name='department-doctors'),
    path('department/<int:pk>/patients/', views.DepartmentPatientsListView.as_view(), name='department-patients'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
