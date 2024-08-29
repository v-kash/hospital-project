

from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound


from .permissions import IsDoctor, IsRelevantPatientOrDoctor, IsDoctorInSameDepartment, IsRelevantPatientOrDoctorForRcords, IsDoctorInDepartment
from .models import Doctor, Patient, PatientRecord, Department
from .serializers import DoctorSerializer, LoginSerializer, PatientSerializer, PatientRecordSerializer, DepartmentSerializer, RegisterSerializer







# Doctor Views
class DoctorListView(generics.ListAPIView):
    #queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user.username}, Is Superuser: {user.is_superuser}, Groups: {user.groups.all()}")
        if user.is_superuser or user.groups.filter(name='Doctor').exists():
            return Doctor.objects.all().only('id', 'user', 'department')
        # If the user doesn't have the correct permissions, return an empty queryset
        return Doctor.objects.none()

@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsDoctor])
def doctor_detail(request, pk):
    
    print("Entering doctor_detail view")

    try:
        doctor = Doctor.objects.get(pk=pk)
    except Doctor.DoesNotExist:
        print("Doctor not found")
        return Response({'detail': 'Doctor not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    # request_user_username = request.user.username
    # doctor_user_username = doctor.user.username

    # print(f"Request user: {request_user_username}, Doctor user: {doctor_user_username}")

    if request.method == 'GET':
        serializer = DoctorSerializer(doctor)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        print("PUT request received")
        if request.user == doctor.user or request.user.is_superuser:
            serializer = DoctorSerializer(doctor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            print("User serializer errors:", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if request.user == doctor.user or request.user.is_superuser:
            user = doctor.user

            # Delete the token associated with the user
            try:
                token = Token.objects.get(user=user)
                token.delete()
            except Token.DoesNotExist:
                print("Token not found for the user")

            doctor.delete()
            user.delete()
            
            return Response({'detail': 'Doctor profile deleted.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'detail': 'You cant delete others record please provide your id .'}, status=status.HTTP_403_FORBIDDEN)

    return Response({'detail': 'you can only change your data only so please send your id if you want to update your records.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

# Patient Views
class PatientListView(generics.ListAPIView):
    #queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctor]

    def get_queryset(self):
        user = self.request.user
        print(f"User: {user.username}, Is Superuser: {user.is_superuser}, Groups: {user.groups.all()}")
        if user.is_superuser or user.groups.filter(name='Doctor').exists():
            return Patient.objects.all().only('id', 'user')
        # If the user doesn't have the correct permissions, return an empty queryset
        return Patient.objects.none()


@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated,IsRelevantPatientOrDoctor])
def patient_detail(request, pk):
    try:
        patient = Patient.objects.get(pk=pk)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)

    # Check permissions for the specific object
    if not IsRelevantPatientOrDoctor().has_object_permission(request, None, patient):
        return Response({"error": "You do not have permission to perform this action.OR It may be not your patient IF YOU ARE DOCTOR OR YOU ARE PATIENT and trying to get another patient record"}, status=status.HTTP_403_FORBIDDEN)

    # GET request: Return patient details
    if request.method == 'GET':
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    
    # PUT request: Update patient details
    elif request.method == 'PATCH':
        serializer = PatientSerializer(patient, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # DELETE request: Delete patient
    elif request.method == 'DELETE':
        user = patient.user
        
        # Check if the requesting user is authorized to delete this patient
        if request.user.is_superuser:
            # Superusers can delete any patient
            pass
        elif request.user.groups.filter(name='Patient').exists():
            # Patients can only delete their own profile
            if request.user != user:
                return Response({"error": "You do not have permission to delete this profile."}, status=status.HTTP_403_FORBIDDEN)
        elif request.user.groups.filter(name='Doctor').exists():
            # Doctors can only delete their assigned patients
            if request.user != patient.assigned_doctor.user:
                return Response({"error": "You do not have permission to delete this patient."}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"error": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        # Delete associated token
        try:
            token = Token.objects.get(user=user)
            token.delete()
        except Token.DoesNotExist:
            print("Token not found for the user")
        
        # Delete the user and patient
        user.delete()
        patient.delete()
        return Response({"message": "Patient deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# PatientRecord Views


class PatientRecordListCreateView(generics.ListCreateAPIView):
    queryset = PatientRecord.objects.all()
    serializer_class = PatientRecordSerializer
    permission_classes = [IsAuthenticated, IsDoctorInSameDepartment]

    def get_queryset(self):
        # Filter records by the doctor's department
        user = self.request.user
        return PatientRecord.objects.filter(department=user.doctor.department)

    def perform_create(self, serializer):
        user = self.request.user
        # Automatically assign the department based on the doctor's department
        serializer.save(department=user.doctor.department)



@api_view(['GET', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, IsRelevantPatientOrDoctorForRcords])
def patient_record_detail(request, pk):
    try:
        print("in patient_record_detail")
        # Fetch the patient
        patient = Patient.objects.get(pk=pk)
        user = request.user
        
        if request.method == 'GET':
            #print("in get req")
            # Fetch all records for the specific patient
            if request.user.is_superuser or hasattr(user, 'patient'):
                #print("i ama patient")
                if request.user.patient == patient or request.user.is_superuser:
                    #print("i ama patient who is logged in")
                    records = PatientRecord.objects.filter(patient=patient)
                    if records.exists():
                        print("here id records if patient", records)
                        serializer = PatientRecordSerializer(records, many=True)
                        return Response(serializer.data)
                    else:
                        return Response({"error": "Record not found."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    return Response({"error": "Record not found because you are sending others id."}, status=status.HTTP_404_NOT_FOUND)
                    
            
            elif request.user.is_superuser or hasattr(user, 'doctor'):
                if patient.assigned_doctor == request.user.doctor or request.user.is_superuser:
                    doctor = request.user.doctor
                    records = PatientRecord.objects.filter(patient=patient, patient__assigned_doctor=doctor)
                    if records.exists():
                        print("here id records if patient", records)
                        serializer = PatientRecordSerializer(records, many=True)
                        return Response(serializer.data)
                    else:
                        return Response({"error": "Record not found ."}, status=status.HTTP_404_NOT_FOUND)
                    
                else:
                    return Response({"error": "Record not found because you are sending others id who is not you patient."}, status=status.HTTP_404_NOT_FOUND)
            else:
                 return Response({"error": "You do not have permission to view this record."}, status=status.HTTP_403_FORBIDDEN)
            


        elif request.method == 'PATCH':
            if patient.assigned_doctor == request.user.doctor or request.user.is_superuser:
                doctor = request.user.doctor
                print("in patch")
            # Extract record ID from the request data
                record_id = request.data.get('record_id')
                try:
                    # Fetch the specific record for the patient
                    record = PatientRecord.objects.get(pk=record_id, patient=patient, patient__assigned_doctor=doctor)
                except PatientRecord.DoesNotExist:
                    return Response({"error": "Record not found or does not belong to this patient or you are not his/her doctor."}, status=status.HTTP_404_NOT_FOUND)

                # Update the record
                serializer = PatientRecordSerializer(record, data=request.data, partial=True, context={'request': request})
                print("serializer created")
                if serializer.is_valid(raise_exception=True):
                    print("validated data")
                    serializer.save()
                    return Response(serializer.data)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                    return Response({"error": "Record not found because you are sending others id who is not you patient."}, status=status.HTTP_404_NOT_FOUND)
            

        elif request.method == 'DELETE':
            print("in delete")
            if patient.assigned_doctor == request.user.doctor or request.user.is_superuser:
                print("i am valid doctor")
                doctor = request.user.doctor
            # Extract record ID from the request data
                record_id = request.data.get('record_id')
                try:
                    # Fetch the specific record for the patient
                    print("inside delete try")
                    record = PatientRecord.objects.get(pk=record_id, patient=patient, patient__assigned_doctor=doctor)
                except PatientRecord.DoesNotExist:
                    return Response({"error": "Record not found or does not belong to this patient or you are not his/her doctor."}, status=status.HTTP_404_NOT_FOUND)

                # Delete the record
                record.delete()
                return Response({
                'success': True,
                'message': 'Patient record successfully deleted.'
            }, status=status.HTTP_204_NO_CONTENT)

            else:
                    return Response({"error": "Record not found because you are sending others id who is not you patient."}, status=status.HTTP_404_NOT_FOUND)
    except Patient.DoesNotExist:
        return Response({"error": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)


# Department Views
from rest_framework.response import Response

class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': 'An error occurred while fetching departments.', 'details': str(e)}, status=500)




class DepartmentDoctorsListView(generics.ListAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated, IsDoctorInDepartment]

    def get_queryset(self):
        department_id = self.kwargs['pk']  # Get department ID from the URL
        return Doctor.objects.filter(department=department_id)

    def get(self, request, *args, **kwargs):
        department_id = self.kwargs['pk']
        if not Department.objects.filter(pk=department_id).exists():
            return Response(
                {"error": "Department with the specified ID {department_id}does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Try to get the doctors (this will trigger permission checks)
            queryset = self.get_queryset()
            if not queryset.exists():
                return Response(
                    {"error": f"No doctors found in department with ID {department_id}."},
                    status=status.HTTP_404_NOT_FOUND
                )
            return super().get(request, *args, **kwargs)
        except PermissionDenied as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_403_FORBIDDEN
            )
    

class DepartmentPatientsListView(generics.ListAPIView):
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated, IsDoctorInDepartment]

    def get_queryset(self):
        department_id = self.kwargs['pk']  # Get department ID from the URL
        return Patient.objects.filter(department_id=department_id)

    def get(self, request, *args, **kwargs):
        department_id = self.kwargs['pk']
        if not Department.objects.filter(pk=department_id).exists():
            return Response(
                {"error": f"Department with ID {department_id} does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        queryset = self.get_queryset()
        if not queryset.exists():
            return Response(
                {"error": f"No patients found in department with ID {department_id}."},
                status=status.HTTP_404_NOT_FOUND
            )
        return super().get(request, *args, **kwargs)





class RegisterView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'User registered successfully Now to know your detail please login'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(serializer.validated_data)



# class DynamicListView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated, IsDoctorInDepartment]

#     def get_serializer_class(self):
#         # Determine the URL path to choose the serializer
#         if 'doctors' in self.request.path:
#             return DoctorSerializer
#         elif 'patients' in self.request.path:
#             return PatientSerializer
#         else:
#             raise NotFound("Endpoint not found.")

#     def get_queryset(self):
#         # Determine the URL path to choose the model
#         department_id = self.kwargs['pk']
#         if 'doctors' in self.request.path:
#             model = Doctor
#         elif 'patients' in self.request.path:
#             model = Patient
#         else:
#             raise NotFound("Endpoint not found.")

#         # Check if the department exists
#         if not Department.objects.filter(pk=department_id).exists():
#             raise NotFound(f"Department with ID {department_id} does not exist.")
        
#         # Return the queryset based on the model
#         return model.objects.filter(department_id=department_id)

#     def get(self, request, *args, **kwargs):
#         # Check if the department has any objects and handle errors
#         queryset = self.get_queryset()
#         if not queryset.exists():
#             return Response(
#                 {"error": f"No records found in department with ID {kwargs['pk']}."},
#                 status=status.HTTP_404_NOT_FOUND
#             )
#         return super().get(request, *args, **kwargs)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user
        try:
            # Delete the user's auth token
            token = Token.objects.get(user=user)
            token.delete()
            
            # return the user information and a success message
            return Response({
                'message': 'Successfully logged out.',
                'user': {
                    'username': user.username
                }
            }, status=status.HTTP_204_NO_CONTENT)
        except Token.DoesNotExist:
            return Response({
                'message': 'No token found for this user.',
                'user': {
                    'id': user.id,
                    'username': user.username
                }
            }, status=status.HTTP_404_NOT_FOUND)