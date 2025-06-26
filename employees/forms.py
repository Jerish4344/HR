from django import forms
from .models import (
    Employee, EmergencyContact, Education, WorkExperience, 
    Skill, Language, EmployeeLanguage
)
from core.models import Department, Store, Role, Document

class EmployeeBasicForm(forms.ModelForm):
    """
    Form for Step 1 of employee creation: Basic Information.
    """
    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'middle_name', 'last_name',
            'date_of_birth', 'gender', 'marital_status', 'blood_group',
            'nationality', 'profile_picture'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(),
            'marital_status': forms.Select(),
            'blood_group': forms.Select(),
            'profile_picture': forms.FileInput(),
        }
        help_texts = {
            'employee_id': 'Unique identifier for the employee.',
            'date_of_birth': 'Please use YYYY-MM-DD format.',
            'profile_picture': 'Upload a clear headshot. Max size 2MB.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif isinstance(field.widget, forms.FileInput):
                field.widget.attrs['class'] = 'form-control'
            elif isinstance(field.widget, forms.DateInput):
                field.widget.attrs['class'] = 'form-control'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EmployeeContactForm(forms.ModelForm):
    """
    Form for Step 2 of employee creation: Contact Information.
    Note: Assumes 'current_address' and 'permanent_address' are TextFields on Employee model
    to match templates.
    """
    class Meta:
        model = Employee
        fields = [
            'primary_phone', 'secondary_phone', 'personal_email', 'official_email',
            'current_address', 'permanent_address'
        ]
        widgets = {
            'personal_email': forms.EmailInput(),
            'official_email': forms.EmailInput(),
            'current_address': forms.Textarea(attrs={'rows': 3}),
            'permanent_address': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'primary_phone': 'The main contact number for the employee.',
            'official_email': 'This will be used for system login and official communication.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EmployeeEmploymentForm(forms.ModelForm):
    """
    Form for Step 3 of employee creation: Employment Information.
    """
    class Meta:
        model = Employee
        fields = [
            'department', 'store', 'role', 'reporting_manager', 'employment_type',
            'date_joined', 'probation_end_date', 'notice_period_days', 'status', 'skills'
        ]
        widgets = {
            'department': forms.Select(),
            'store': forms.Select(),
            'role': forms.Select(),
            'reporting_manager': forms.Select(),
            'employment_type': forms.Select(),
            'date_joined': forms.DateInput(attrs={'type': 'date'}),
            'probation_end_date': forms.DateInput(attrs={'type': 'date'}),
            'status': forms.Select(),
            'skills': forms.SelectMultiple(attrs={'size': '5'}),
        }
        help_texts = {
            'reporting_manager': 'Select the manager this employee reports to.',
            'probation_end_date': 'Date when the probation period ends.',
            'notice_period_days': 'Number of days required for notice period.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].queryset = Department.objects.filter(is_active=True)
        self.fields['store'].queryset = Store.objects.filter(is_active=True)
        self.fields['role'].queryset = Role.objects.filter(is_active=True)
        self.fields['reporting_manager'].queryset = Employee.objects.filter(is_deleted=False, status='active')
        self.fields['skills'].queryset = Skill.objects.filter(is_active=True)
        
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
            
            if not isinstance(field.widget, forms.SelectMultiple):
                field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EmployeeFinancialForm(forms.ModelForm):
    """
    Form for Step 4 of employee creation: Financial Information.
    """
    class Meta:
        model = Employee
        fields = [
            'bank_name', 'bank_account_number', 'ifsc_code', 'pan_number',
            'aadhar_number', 'uan_number', 'esic_number'
        ]
        help_texts = {
            'pan_number': 'Permanent Account Number.',
            'aadhar_number': '12-digit unique identification number.',
            'uan_number': 'Universal Account Number for EPF.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EmployeeDocumentForm(forms.ModelForm):
    """
    Form for uploading employee-related documents.
    This form is based on the core 'Document' model.
    """
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'document_type', 'expiry_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'expiry_date': forms.DateInput(attrs={'type': 'date'}),
            'document_type': forms.Select(),
        }
        help_texts = {
            'expiry_date': 'Optional: for documents like passports, visas, etc.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            else:
                field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EmergencyContactForm(forms.ModelForm):
    """
    Form for adding/editing an employee's emergency contact.
    """
    class Meta:
        model = EmergencyContact
        fields = ['name', 'relationship', 'primary_phone', 'secondary_phone', 'email', 'address', 'is_primary']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'email': forms.EmailInput(),
            'is_primary': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class EducationForm(forms.ModelForm):
    """
    Form for adding/editing an employee's education details.
    """
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'grade', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class WorkExperienceForm(forms.ModelForm):
    """
    Form for adding/editing an employee's work experience.
    """
    class Meta:
        model = WorkExperience
        fields = ['company_name', 'job_title', 'start_date', 'end_date', 'description', 'is_current']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
            'is_current': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
                field.widget.attrs['placeholder'] = field.label or field_name.replace('_', ' ').title()


class LanguageProficiencyForm(forms.ModelForm):
    """
    Form for adding/editing an employee's language proficiency.
    """
    class Meta:
        model = EmployeeLanguage
        fields = ['language', 'reading', 'writing', 'speaking']
        widgets = {
            'language': forms.Select(),
            'reading': forms.Select(),
            'writing': forms.Select(),
            'speaking': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['language'].queryset = Language.objects.all()
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs['class'] = 'form-select'
            elif not isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-control'
