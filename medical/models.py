from django.db import models
from django.contrib.auth.models import User

class Department(models.Model):
    name = models.CharField(max_length=100)
    diagnostics = models.TextField()
    location = models.CharField(max_length=255)
    specialization = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, related_name='doctors', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='patients')
    assigned_doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='patients')

    def __str__(self):
        return self.user.username

class PatientRecord(models.Model):
    record_id = models.AutoField(primary_key=True)
    patient = models.ForeignKey(Patient, related_name='records', on_delete=models.CASCADE)
    created_date = models.DateTimeField(auto_now_add=True)
    diagnostics = models.TextField()
    observations = models.TextField()
    treatments = models.TextField()
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    misc = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'Record {self.record_id} for {self.patient.user.username}'
