from medical.models import Department, Doctor, Patient, PatientRecord
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
# Create and save Department instances

class Command(BaseCommand):
    help = 'Populate the database with sample data'

    def handle(self, *args, **options):
        departments = [
            Department(name="Cardiology", diagnostics="Heart issues", location="Building A", specialization="Heart"),
            Department(name="Neurology", diagnostics="Brain issues", location="Building B", specialization="Brain"),
            Department(name="Orthopedics", diagnostics="Bone issues", location="Building C", specialization="Bones"),
        ]

        for dept in departments:
            dept.save()
            

        # Create and save Doctor instances
        doctors = [
            Doctor(user=User.objects.create(username='dr_john', first_name='John', last_name='Doe', password='password'), department=departments[0]),
            Doctor(user=User.objects.create(username='dr_jane', first_name='Jane', last_name='Smith', password='password'), department=departments[0]),
            Doctor(user=User.objects.create(username='dr_alex', first_name='Alex', last_name='Johnson', password='password'), department=departments[1]),
            Doctor(user=User.objects.create(username='dr_susan', first_name='Susan', last_name='Lee', password='password'), department=departments[1]),
            Doctor(user=User.objects.create(username='dr_mike', first_name='Mike', last_name='Brown', password='password'), department=departments[2]),
        ]

        for doctor in doctors:
            doctor.user.set_password('password')  # Ensure the password is hashed
            doctor.user.save()
            doctor.save()

        # Create and save Patient instances
        patients = [
            Patient(user=User.objects.create(username='patient_1', first_name='Alice', last_name='Wong', password='password'), department=departments[0], assigned_doctor=doctors[0]),
            Patient(user=User.objects.create(username='patient_2', first_name='Bob', last_name='Nguyen', password='password'), department=departments[0], assigned_doctor=doctors[1]),
            Patient(user=User.objects.create(username='patient_3', first_name='Charlie', last_name='Kim', password='password'), department=departments[0], assigned_doctor=doctors[0]),
            Patient(user=User.objects.create(username='patient_4', first_name='David', last_name='Patel', password='password'), department=departments[1], assigned_doctor=doctors[2]),
            Patient(user=User.objects.create(username='patient_5', first_name='Eva', last_name='Garcia', password='password'), department=departments[1], assigned_doctor=doctors[3]),
            Patient(user=User.objects.create(username='patient_6', first_name='Frank', last_name='Harris', password='password'), department=departments[1], assigned_doctor=doctors[2]),
            Patient(user=User.objects.create(username='patient_7', first_name='Grace', last_name='Martinez', password='password'), department=departments[2], assigned_doctor=doctors[4]),
            Patient(user=User.objects.create(username='patient_8', first_name='Hannah', last_name='Lopez', password='password'), department=departments[2], assigned_doctor=doctors[4]),
            Patient(user=User.objects.create(username='patient_9', first_name='Ivy', last_name='Davis', password='password'), department=departments[0], assigned_doctor=doctors[0]),
            Patient(user=User.objects.create(username='patient_10', first_name='Jack', last_name='Miller', password='password'), department=departments[0], assigned_doctor=doctors[1]),
            Patient(user=User.objects.create(username='patient_11', first_name='Karen', last_name='Wilson', password='password'), department=departments[1], assigned_doctor=doctors[3]),
            Patient(user=User.objects.create(username='patient_12', first_name='Leo', last_name='Moore', password='password'), department=departments[1], assigned_doctor=doctors[2]),
            Patient(user=User.objects.create(username='patient_13', first_name='Mia', last_name='Taylor', password='password'), department=departments[2], assigned_doctor=doctors[4]),
            Patient(user=User.objects.create(username='patient_14', first_name='Nina', last_name='Anderson', password='password'), department=departments[2], assigned_doctor=doctors[4]),
            Patient(user=User.objects.create(username='patient_15', first_name='Oscar', last_name='Thomas', password='password'), department=departments[2], assigned_doctor=doctors[4]),
        ]

        for patient in patients:
            patient.user.set_password('password')  # Ensure the password is hashed
            patient.user.save()
            patient.save()

        # Create and save PatientRecord instances
        patient_records = [
            PatientRecord(patient=patients[0], created_date='2023-01-15', diagnostics="Hypertension", observations="High BP", treatments="Medication", department=departments[0], misc="None"),
            PatientRecord(patient=patients[1], created_date='2023-02-10', diagnostics="Arrhythmia", observations="Irregular heartbeat", treatments="Pacemaker", department=departments[0], misc="None"),
            PatientRecord(patient=patients[2], created_date='2023-03-05', diagnostics="Coronary Artery Disease", observations="Chest pain", treatments="Surgery", department=departments[0], misc="None"),
            PatientRecord(patient=patients[3], created_date='2023-04-20', diagnostics="Epilepsy", observations="Seizures", treatments="Medication", department=departments[1], misc="None"),
            PatientRecord(patient=patients[4], created_date='2023-05-25', diagnostics="Migraine", observations="Headaches", treatments="Medication", department=departments[1], misc="None"),
            PatientRecord(patient=patients[5], created_date='2023-06-15', diagnostics="Stroke", observations="Weakness", treatments="Therapy", department=departments[1], misc="None"),
            PatientRecord(patient=patients[6], created_date='2023-07-05', diagnostics="Fracture", observations="Broken leg", treatments="Casting", department=departments[2], misc="None"),
            PatientRecord(patient=patients[7], created_date='2023-08-10', diagnostics="Arthritis", observations="Joint pain", treatments="Medication", department=departments[2], misc="None"),
            PatientRecord(patient=patients[8], created_date='2023-09-01', diagnostics="Congestive Heart Failure", observations="Shortness of breath", treatments="Surgery", department=departments[0], misc="None"),
            PatientRecord(patient=patients[9], created_date='2023-10-15', diagnostics="Myocardial Infarction", observations="Chest pain", treatments="Stent", department=departments[0], misc="None"),
            PatientRecord(patient=patients[10], created_date='2023-11-05', diagnostics="Parkinson's Disease", observations="Tremors", treatments="Therapy", department=departments[1], misc="None"),
            PatientRecord(patient=patients[11], created_date='2023-12-01', diagnostics="Alzheimer's Disease", observations="Memory loss", treatments="Medication", department=departments[1], misc="None"),
            PatientRecord(patient=patients[12], created_date='2023-12-15', diagnostics="Osteoporosis", observations="Weak bones", treatments="Medication", department=departments[2], misc="None"),
            PatientRecord(patient=patients[13], created_date='2024-01-10', diagnostics="Tendonitis", observations="Inflammation", treatments="Therapy", department=departments[2], misc="None"),
            PatientRecord(patient=patients[14], created_date='2024-02-05', diagnostics="Dislocation", observations="Shoulder dislocation", treatments="Reduction", department=departments[2], misc="None"),
        ]

        for record in patient_records:
            record.save()
