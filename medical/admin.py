# medical/admin.py

from django.contrib import admin
from .models import Department, Doctor, Patient, PatientRecord

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'diagnostics', 'location', 'specialization')

@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'department')

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('pk','user', 'department', 'assigned_doctor')

@admin.register(PatientRecord)
class PatientRecordAdmin(admin.ModelAdmin):
    list_display = ('pk','patient', 'created_date','diagnostics', 'observations', 'treatments', 'department', 'misc')

