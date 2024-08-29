from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import Doctor

class IsDoctor(BasePermission):
    """
    Custom permission to only allow doctors to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is in the 'doctor' group
        user = request.user
        return request.user.is_superuser or hasattr(user, 'doctor') #request.user.groups.filter(name='Doctor').exists()



class IsRelevantPatientOrDoctor(BasePermission):
    """
    Custom permission to only allow the relevant patient, their assigned doctor, or a superuser to access the patient's details.
    """

    def has_object_permission(self, request, view, obj):
        # Allow access if the user is a superuser
        if request.user.is_superuser:
            return True
        
        # Allow access if the user is the patient
        if obj.user == request.user:
            return True

        # Allow access if the user is the assigned doctor
        if request.user.groups.filter(name='Doctor').exists() and obj.assigned_doctor.user == request.user:
            return True

        # Deny access otherwise
        return False



class IsDoctorInSameDepartment(BasePermission):
    def has_permission(self, request, view):
        # Check if the user is a doctor
        return request.user.is_superuser or hasattr(request.user, 'doctor')

    def has_object_permission(self, request, view, obj):
        # Check if the doctor's department matches the record's department
        return obj.department == request.user.doctor.department





class IsRelevantPatientOrDoctorForRcords(BasePermission):
    def has_permission(self, request, view):
        # Allow access to authenticated users only
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow superusers to access any object
        if request.user.is_superuser:
            return True
        
        # For GET requests, check if the user is the patient or a relevant doctor
        if request.method == 'GET':
            return (request.user == obj.patient.user or
                    (request.user.is_authenticated and hasattr(request.user, 'doctor') and request.user.doctor.department == obj.department))

        # For PATCH and DELETE requests, check if the user is a doctor in the same department
        if request.method in ['PATCH', 'DELETE']:
            return (request.user.is_authenticated and hasattr(request.user, 'doctor') and request.user.doctor.department == obj.department)

        return False






class IsDoctorInDepartment(BasePermission):
    def has_permission(self, request, view):
        # Allow superusers to access the endpoint
        if request.user and request.user.is_superuser:
            return True
        
        department_id = view.kwargs.get('pk')
        try:
            doctor = Doctor.objects.get(user=request.user)
        except Doctor.DoesNotExist:
            raise PermissionDenied("You are not authorized to access this department.")

        # Check if the doctor's department matches the department ID in the URL
        if doctor.department_id != department_id:
            raise PermissionDenied(f'You do not have permission to access doctors in this department because you are in {doctor.department.name} department your id is {doctor.department_id}.')

        return True

