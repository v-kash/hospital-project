
from django.core.exceptions import ValidationError
from rest_framework import serializers
from .models import Doctor, Patient, PatientRecord, Department
from django.contrib.auth.models import User, Group 
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'password']
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def update(self, instance, validated_data):
        # Update the user instance
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        
        return super(UserSerializer, self).update(instance, validated_data)


class DoctornameSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # This will return the username of the doctor

    class Meta:
        model = Doctor
        fields = ['user']

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer to handle the related User object

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'department']

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)  # Extract nested user data
        department_id = validated_data.get('department', None)

        if department_id and not Department.objects.filter(id=department_id.id).exists():
            raise ValidationError({'department': 'Department does not exist.try among this values [6,7,8]'})
        instance = super().update(instance, validated_data)

        if user_data:
            user = instance.user
            user_serializer = UserSerializer(user, data=user_data, partial=True)

            if 'first_name' in user_data and user_data['first_name'] == '':
                user_data.pop('first_name')
            if 'last_name' in user_data and user_data['last_name'] == '':
                user_data.pop('last_name')

            if user_serializer.is_valid():
                user_serializer.save()  # Update User data if valid
            else:
                raise ValidationError(user_serializer.errors)
            
        return instance


class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()  # Nested serializer to handle the related User object
    assigned_doctor_name = serializers.CharField(source='assigned_doctor.user.username', read_only=True)

    class Meta:
        model = Patient
        fields = ['id', 'user', 'department', 'assigned_doctor','assigned_doctor_name' ]

    def update(self, instance, validated_data):
        # Extract nested user data
        user_data = validated_data.pop('user', None)
        request_user = self.context['request'].user

        # Superuser can update any field
        if request_user.is_superuser:
            if user_data:
                user = instance.user
                user_serializer = UserSerializer(user, data=user_data, partial=True)
                if 'first_name' in user_data and user_data['first_name'] == '':
                    user_data.pop('first_name')
                if 'last_name' in user_data and user_data['last_name'] == '':
                    user_data.pop('last_name')

                if user_serializer.is_valid():
                    user_serializer.save()
            return super().update(instance, validated_data)

        # Restrict fields based on user role
        if request_user.groups.filter(name='Patient').exists():
            # If the user is a patient, allow only user-related updates
            if user_data:
                user = instance.user
                user_serializer = UserSerializer(user, data=user_data, partial=True)

                if 'first_name' in user_data and user_data['first_name'] == '':
                    user_data.pop('first_name')
                if 'last_name' in user_data and user_data['last_name'] == '':
                    user_data.pop('last_name')

                if user_serializer.is_valid():
                    user_serializer.save()
            else:
                raise serializers.ValidationError("Patients are not allowed to update department or assigned doctor.")
        elif request_user.groups.filter(name='Doctor').exists():
            # If the user is a doctor, allow only department or assigned doctor updates
            allowed_fields = ['department', 'assigned_doctor']
            update_data = {key: value for key, value in validated_data.items() if key in allowed_fields}
            print(update_data)
            if update_data:
                instance = super().update(instance, update_data)
            else:
                raise serializers.ValidationError("Doctors are not allowed to update user information.")


        return instance




class PatientRecordSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.user.username', read_only=True)
    class Meta:
        model = PatientRecord
        fields = ['record_id', 'patient', 'patient_name' ,'created_date', 'diagnostics', 'observations', 'treatments', 'department', 'misc']

    def validate(self, data):
        """
        Validate the provided data for creating a PatientRecord.
        """
        print("in validating serializer")
        request_method = self.context['request'].method
        # Check if patient field is provided and is a valid ID
        if request_method == 'POST':
            print("in validating serializer post")
            if 'patient' not in data:
                raise serializers.ValidationError({"patient": "This field is required."})
            
            patient_id = data['patient'].id if isinstance(data['patient'], Patient) else data['patient']
            if not Patient.objects.filter(pk=patient_id).exists():
                raise serializers.ValidationError({"patient": "Invalid patient ID."})
            
        # if request_method in ['PATCH', 'PUT']:
        #     print("in validating serializer patch or put")
        # # For PATCH/PUT requests, remove patient and department fields from validation
            
        #     data.pop('patient', None)
        #     data.pop('department', None)
        
        return data

    def create(self, validated_data):
        # Automatically assign the department based on the doctor's department
        validated_data['department'] = self.context['request'].user.doctor.department
        return super().create(validated_data)

    def update(self, instance, validated_data):
       
        
        # Allow updates only for relevant fields; doctor should not change the patient or department directly.
        if 'patient' in validated_data:
            raise serializers.ValidationError({"patient": "You cannot change the patient of an existing record so remove it from field."})
        
        # If the doctor is updating, ensure the department remains consistent
        if 'department' in validated_data:
            raise serializers.ValidationError({"department": "You cannot change the department of an existing record so remove it from field."})
        
        # Handle other updates normally
        return super().update(instance, validated_data)


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name', 'diagnostics', 'location', 'specialization']





class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)  # Make password write-only

    def validate(self, data):
        # Authenticate the user with the provided credentials
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            # Create or retrieve the user's token
            token, created = Token.objects.get_or_create(user=user)

            role_id = {}

            for role in ['patient', 'doctor']:
                if hasattr(user, role):
                    role_id[f'{role}_id'] = getattr(user, role).id
            response_data = {
                'token': token.key,
                'user': {
                    'user_id': user.id,
                    **role_id,
                    'username': user.username,
                    'groups': [group.name for group in user.groups.all()]
                }
            }
            return response_data
        # Raise validation error if credentials are invalid
        raise serializers.ValidationError("Invalid credentials. Please try again.")











class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    user_type = serializers.ChoiceField(choices=['doctor', 'patient'])
    department = serializers.IntegerField()
    assigned_doctor = serializers.IntegerField(required=False)  # Only for patients

    def validate(self, data):
        user_type = data.get('user_type')
        department_id = data.get('department')
        value = data.get('username')

        if user_type == 'doctor':
            # Check if the dr_username already exists
            if User.objects.filter(username=f'dr_{value}').exists():
                raise serializers.ValidationError("This username is already taken for a doctor. Please choose another.")
        else:
            # Check if the username already exists
            if User.objects.filter(username=value).exists():
                raise serializers.ValidationError("This username is already taken. Please choose another.")

        
        # Check if the department exists
        if not Department.objects.filter(id=department_id).exists():
            raise serializers.ValidationError("The specified department does not exist. please select from given value [6, 7, 8]as id")
        
        # Additional validation if the user is a patient
        if user_type == 'patient':
            assigned_doctor_id = data.get('assigned_doctor')
            
            if assigned_doctor_id:
                # Check if the assigned doctor exists
                if not Doctor.objects.filter(id=assigned_doctor_id).exists():
                    raise serializers.ValidationError("The specified assigned doctor does not exist please select from given value [1,2,3,4,5] as id .")
                
                # Check if the doctor's department matches the patient's department
                doctor = Doctor.objects.get(id=assigned_doctor_id)
                if doctor.department_id != department_id:
                    raise serializers.ValidationError("THIS FIELD IS OPTIONAL   The assigned doctor does not belong to the same department as the patient try this combo for [ departmen -> 6 use assigned doctor -> 1 or 2 ] , [ for dep -> 7 use assigned doctor -> 3 or 4]  and [ dep 8 -> use assigned doctor -> 5 ]  .")
        
        return data

    def create(self, validated_data):
        user_type = validated_data.pop('user_type')
        username = validated_data['username']
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        
        # Create user with additional fields
        if user_type == 'doctor':
            username = f"dr_{username}"
        user = User.objects.create_user(
            username=username,
            password=validated_data['password'],
            first_name=first_name,
            last_name=last_name
        )
        
        # Create user-specific model instance
        if user_type == 'doctor':
            Doctor.objects.create(user=user, department_id=validated_data['department'])
            # Assign to doctor group
            doctor_group, _ = Group.objects.get_or_create(name='Doctor')
            user.groups.add(doctor_group)
        elif user_type == 'patient':
            assigned_doctor_id = validated_data.get('assigned_doctor')  # Can be None
            Patient.objects.create(
                user=user,
                department_id=validated_data['department'],
                assigned_doctor_id=assigned_doctor_id
            )
            # Assign to patient group
            patient_group, _ = Group.objects.get_or_create(name='Patient')
            user.groups.add(patient_group)
        
        return user
