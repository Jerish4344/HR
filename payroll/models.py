from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from decimal import Decimal

from core.models import TimeStampedModel, SoftDeleteModel
from employees.models import Employee


class SalaryComponentType(models.TextChoices):
    EARNING = 'earning', _('Earning')
    DEDUCTION = 'deduction', _('Deduction')
    REIMBURSEMENT = 'reimbursement', _('Reimbursement')
    BONUS = 'bonus', _('Bonus')
    TAX = 'tax', _('Tax')


class SalaryComponent(TimeStampedModel, SoftDeleteModel):
    """
    Model to define different salary components like Basic, HRA, etc.
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    description = models.TextField(blank=True, null=True)
    component_type = models.CharField(
        max_length=20,
        choices=SalaryComponentType.choices,
        default=SalaryComponentType.EARNING
    )
    is_taxable = models.BooleanField(
        default=True,
        help_text=_("Whether this component is taxable")
    )
    is_fixed = models.BooleanField(
        default=True,
        help_text=_("Whether this is a fixed component or calculated")
    )
    calculation_formula = models.TextField(
        blank=True, 
        null=True,
        help_text=_("Formula to calculate this component (if not fixed)")
    )
    is_percentage = models.BooleanField(
        default=False,
        help_text=_("Whether this component is calculated as a percentage of another component")
    )
    percentage_of = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='percentage_components',
        help_text=_("Component this is a percentage of")
    )
    percentage_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage value if this is a percentage-based component")
    )
    is_active = models.BooleanField(default=True)
    display_order = models.PositiveIntegerField(
        default=0,
        help_text=_("Order in which to display this component on salary slips")
    )
    
    class Meta:
        ordering = ['component_type', 'display_order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"
    
    def calculate_value(self, base_value=None, salary_structure=None):
        """
        Calculate the value of this component based on its configuration.
        
        Args:
            base_value: The base value to calculate from (for fixed components)
            salary_structure: The full salary structure (for calculated components)
        
        Returns:
            Decimal: The calculated value of this component
        """
        if not self.is_active:
            return Decimal('0.00')
        
        if self.is_fixed:
            return base_value or Decimal('0.00')
        
        if self.is_percentage and self.percentage_of and salary_structure:
            # Get the value of the referenced component
            ref_component_code = self.percentage_of.code
            ref_value = salary_structure.get(ref_component_code, Decimal('0.00'))
            
            # Calculate percentage
            return (ref_value * self.percentage_value) / Decimal('100.00')
        
        # For more complex calculations, we would evaluate the formula here
        # This is a simplified implementation
        return Decimal('0.00')


class Salary(TimeStampedModel, SoftDeleteModel):
    """
    Model to store employee salary information.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salaries'
    )
    effective_from = models.DateField()
    effective_to = models.DateField(null=True, blank=True)
    gross_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    net_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Basic salary component")
    )
    is_current = models.BooleanField(
        default=True,
        help_text=_("Whether this is the current active salary")
    )
    salary_structure = models.JSONField(
        default=dict,
        help_text=_("Detailed breakdown of salary components")
    )
    payment_mode = models.CharField(
        max_length=50,
        default='bank_transfer',
        help_text=_("Mode of salary payment")
    )
    bank_account = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Bank account for salary transfer")
    )
    remarks = models.TextField(blank=True, null=True)
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_salaries'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-effective_from', '-created_at']
        indexes = [
            models.Index(fields=['employee', 'effective_from']),
            models.Index(fields=['is_current']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.gross_salary} (from {self.effective_from})"
    
    def save(self, *args, **kwargs):
        # If this is marked as current, make all other salary records for this employee not current
        if self.is_current:
            Salary.objects.filter(
                employee=self.employee,
                is_current=True
            ).exclude(pk=self.pk).update(is_current=False)
        
        super().save(*args, **kwargs)
    
    @property
    def annual_salary(self):
        """Calculate annual salary based on gross salary."""
        return self.gross_salary * 12
    
    def get_component_value(self, component_code):
        """Get the value of a specific salary component."""
        return self.salary_structure.get(component_code, Decimal('0.00'))
    
    def calculate_net_salary(self):
        """Calculate net salary based on gross salary and deductions."""
        gross = self.gross_salary
        deductions = sum(
            Decimal(str(value)) for key, value in self.salary_structure.items()
            if key.startswith('deduction_') or key.startswith('tax_')
        )
        return gross - deductions


class PayrollStatus(models.TextChoices):
    DRAFT = 'draft', _('Draft')
    PROCESSING = 'processing', _('Processing')
    COMPLETED = 'completed', _('Completed')
    APPROVED = 'approved', _('Approved')
    PAID = 'paid', _('Paid')
    CANCELLED = 'cancelled', _('Cancelled')


class PayrollProcessing(TimeStampedModel):
    """
    Model to manage monthly payroll processing.
    """
    month = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)]
    )
    year = models.PositiveIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=PayrollStatus.choices,
        default=PayrollStatus.DRAFT
    )
    total_employees = models.PositiveIntegerField(default=0)
    total_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)]
    )
    processed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        related_name='processed_payrolls'
    )
    approved_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_payrolls'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    payment_date = models.DateField(null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    is_locked = models.BooleanField(
        default=False,
        help_text=_("Whether this payroll is locked for editing")
    )
    
    class Meta:
        ordering = ['-year', '-month']
        unique_together = ['month', 'year']
        indexes = [
            models.Index(fields=['month', 'year']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"Payroll - {self.get_month_name()} {self.year} ({self.get_status_display()})"
    
    def get_month_name(self):
        """Get the name of the month."""
        import calendar
        return calendar.month_name[self.month]
    
    def process_payroll(self):
        """Process payroll for all eligible employees."""
        if self.status != PayrollStatus.DRAFT:
            raise ValueError("Payroll can only be processed from draft status")
        
        # Mark as processing
        self.status = PayrollStatus.PROCESSING
        self.save()
        
        try:
            # Get all active employees
            active_employees = Employee.objects.filter(
                is_deleted=False,
                status='active',
                date_joined__lte=self.end_date
            )
            
            self.total_employees = active_employees.count()
            total_amount = Decimal('0.00')
            
            # Process each employee
            for employee in active_employees:
                # Get current salary
                try:
                    salary = Salary.objects.get(
                        employee=employee,
                        is_current=True,
                        effective_from__lte=self.end_date
                    )
                    
                    # Create salary slip
                    slip = SalarySlip.objects.create(
                        employee=employee,
                        payroll=self,
                        salary=salary,
                        gross_amount=salary.gross_salary,
                        net_amount=salary.net_salary,
                        payment_status='pending',
                        salary_components=salary.salary_structure
                    )
                    
                    # Calculate deductions based on attendance, etc.
                    # This would be more complex in a real system
                    
                    # Update total amount
                    total_amount += salary.net_salary
                    
                except Salary.DoesNotExist:
                    # Log that employee has no salary defined
                    pass
            
            # Update payroll with totals
            self.total_amount = total_amount
            self.status = PayrollStatus.COMPLETED
            self.save()
            
            return True
        
        except Exception as e:
            # If any error occurs, mark as draft again
            self.status = PayrollStatus.DRAFT
            self.save()
            raise e
    
    def approve(self, approver):
        """Approve the processed payroll."""
        if self.status != PayrollStatus.COMPLETED:
            raise ValueError("Only completed payrolls can be approved")
        
        self.status = PayrollStatus.APPROVED
        self.approved_by = approver
        self.approved_at = timezone.now()
        self.save()
        
        # Update all salary slips to approved
        SalarySlip.objects.filter(payroll=self).update(payment_status='approved')
    
    def mark_paid(self, payment_date=None):
        """Mark the payroll as paid."""
        if self.status != PayrollStatus.APPROVED:
            raise ValueError("Only approved payrolls can be marked as paid")
        
        self.status = PayrollStatus.PAID
        self.payment_date = payment_date or timezone.now().date()
        self.save()
        
        # Update all salary slips to paid
        SalarySlip.objects.filter(payroll=self).update(
            payment_status='paid',
            payment_date=self.payment_date
        )
    
    def lock(self):
        """Lock the payroll to prevent further changes."""
        self.is_locked = True
        self.save()


class SalarySlip(TimeStampedModel):
    """
    Model to store individual salary slips for employees.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='salary_slips'
    )
    payroll = models.ForeignKey(
        PayrollProcessing,
        on_delete=models.CASCADE,
        related_name='salary_slips'
    )
    salary = models.ForeignKey(
        Salary,
        on_delete=models.SET_NULL,
        null=True,
        related_name='salary_slips'
    )
    slip_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        help_text=_("Unique salary slip number")
    )
    gross_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    net_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    payment_status = models.CharField(
        max_length=20,
        default='pending',
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('paid', 'Paid'),
            ('failed', 'Failed'),
            ('cancelled', 'Cancelled'),
        ]
    )
    payment_date = models.DateField(null=True, blank=True)
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Reference number for the payment transaction")
    )
    salary_components = models.JSONField(
        default=dict,
        help_text=_("Detailed breakdown of salary components")
    )
    attendance_summary = models.JSONField(
        default=dict,
        help_text=_("Summary of attendance for the pay period")
    )
    remarks = models.TextField(blank=True, null=True)
    is_email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-payroll__year', '-payroll__month', 'employee__employee_id']
        indexes = [
            models.Index(fields=['employee', 'payment_status']),
            models.Index(fields=['payroll', 'payment_status']),
        ]
    
    def __str__(self):
        return f"Salary Slip - {self.employee.full_name} - {self.payroll.get_month_name()} {self.payroll.year}"
    
    def save(self, *args, **kwargs):
        # Generate slip number if not provided
        if not self.slip_number:
            self.slip_number = self.generate_slip_number()
        
        super().save(*args, **kwargs)
    
    def generate_slip_number(self):
        """Generate a unique slip number."""
        prefix = f"SL-{self.payroll.year}{self.payroll.month:02d}-"
        
        # Get the last slip number with this prefix
        last_slip = SalarySlip.objects.filter(
            slip_number__startswith=prefix
        ).order_by('-slip_number').first()
        
        if last_slip and last_slip.slip_number:
            try:
                # Extract the number part and increment
                last_number = int(last_slip.slip_number.split('-')[-1])
                new_number = last_number + 1
            except (ValueError, IndexError):
                new_number = 1
        else:
            new_number = 1
        
        return f"{prefix}{new_number:04d}"
    
    def send_email(self):
        """Send salary slip by email to the employee."""
        if self.is_email_sent:
            return False
        
        # Email sending logic would go here
        # This is a placeholder for actual implementation
        
        self.is_email_sent = True
        self.email_sent_at = timezone.now()
        self.save()
        
        return True
    
    def get_earnings(self):
        """Get all earnings from salary components."""
        return {k: v for k, v in self.salary_components.items() 
                if k.startswith('earning_')}
    
    def get_deductions(self):
        """Get all deductions from salary components."""
        return {k: v for k, v in self.salary_components.items() 
                if k.startswith('deduction_')}
    
    def get_taxes(self):
        """Get all tax deductions from salary components."""
        return {k: v for k, v in self.salary_components.items() 
                if k.startswith('tax_')}


class TaxDeduction(TimeStampedModel):
    """
    Model to manage tax deductions for employees.
    """
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name='tax_deductions'
    )
    financial_year = models.CharField(
        max_length=9,  # Format: YYYY-YYYY
        help_text=_("Financial year for tax calculation (e.g., 2023-2024)")
    )
    tax_regime = models.CharField(
        max_length=20,
        choices=[
            ('old', 'Old Regime'),
            ('new', 'New Regime'),
        ],
        default='old',
        help_text=_("Tax regime chosen by the employee")
    )
    gross_income = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Total gross income for the year")
    )
    taxable_income = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Total taxable income after exemptions")
    )
    tax_deductions = models.JSONField(
        default=dict,
        help_text=_("Breakdown of tax deductions under different sections")
    )
    total_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text=_("Total tax calculated for the year")
    )
    tax_paid_to_date = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Tax already paid/deducted till date")
    )
    remaining_tax = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Remaining tax to be paid")
    )
    monthly_deduction = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Monthly tax deduction amount")
    )
    is_finalized = models.BooleanField(
        default=False,
        help_text=_("Whether tax calculation is finalized for the year")
    )
    remarks = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-financial_year', 'employee__employee_id']
        unique_together = ['employee', 'financial_year']
        indexes = [
            models.Index(fields=['employee', 'financial_year']),
            models.Index(fields=['financial_year']),
        ]
    
    def __str__(self):
        return f"Tax Deduction - {self.employee.full_name} - {self.financial_year}"
    
    def calculate_tax(self):
        """
        Calculate tax based on income and deductions.
        This is a simplified implementation - actual tax calculation would be more complex.
        """
        # Calculate taxable income
        gross = self.gross_income
        deductions = sum(Decimal(str(value)) for value in self.tax_deductions.values())
        taxable = max(gross - deductions, Decimal('0.00'))
        self.taxable_income = taxable
        
        # Calculate tax based on regime and tax slabs
        # This is highly simplified - actual implementation would use proper tax slabs
        if self.tax_regime == 'old':
            if taxable <= Decimal('250000'):
                tax = Decimal('0')
            elif taxable <= Decimal('500000'):
                tax = (taxable - Decimal('250000')) * Decimal('0.05')
            elif taxable <= Decimal('1000000'):
                tax = Decimal('12500') + (taxable - Decimal('500000')) * Decimal('0.2')
            else:
                tax = Decimal('112500') + (taxable - Decimal('1000000')) * Decimal('0.3')
        else:  # new regime
            if taxable <= Decimal('300000'):
                tax = Decimal('0')
            elif taxable <= Decimal('600000'):
                tax = (taxable - Decimal('300000')) * Decimal('0.05')
            elif taxable <= Decimal('900000'):
                tax = Decimal('15000') + (taxable - Decimal('600000')) * Decimal('0.1')
            elif taxable <= Decimal('1200000'):
                tax = Decimal('45000') + (taxable - Decimal('900000')) * Decimal('0.15')
            elif taxable <= Decimal('1500000'):
                tax = Decimal('90000') + (taxable - Decimal('1200000')) * Decimal('0.2')
            else:
                tax = Decimal('150000') + (taxable - Decimal('1500000')) * Decimal('0.3')
        
        # Add cess
        tax = tax + (tax * Decimal('0.04'))  # 4% cess
        
        self.total_tax = tax
        self.remaining_tax = max(tax - self.tax_paid_to_date, Decimal('0.00'))
        
        # Calculate monthly deduction for remaining months
        # Assuming financial year is from April to March
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        # Parse financial year (format: YYYY-YYYY)
        fy_start_year = int(self.financial_year.split('-')[0])
        fy_end_year = int(self.financial_year.split('-')[1])
        
        # Calculate remaining months in the financial year
        if current_year == fy_start_year:
            # We're in the first year of the financial year (Apr-Dec)
            remaining_months = 12 - current_month + 3  # +3 for Jan-Mar of next year
        else:
            # We're in the second year of the financial year (Jan-Mar)
            remaining_months = 3 - current_month
        
        # Ensure at least 1 month for calculation
        remaining_months = max(remaining_months, 1)
        
        # Calculate monthly deduction
        self.monthly_deduction = self.remaining_tax / Decimal(remaining_months)
        
        self.save()
        
        return self.total_tax
    
    def finalize(self):
        """Finalize tax calculation for the year."""
        self.is_finalized = True
        self.save()
    
    def get_tax_projection(self):
        """Get monthly tax projection for the financial year."""
        if not self.is_finalized:
            self.calculate_tax()
        
        # Parse financial year
        fy_start_year = int(self.financial_year.split('-')[0])
        fy_end_year = int(self.financial_year.split('-')[1])
        
        # Create monthly projection
        projection = []
        monthly_tax = self.total_tax / Decimal('12')
        
        # April to December of first year
        for month in range(4, 13):
            projection.append({
                'month': f"{month:02d}-{fy_start_year}",
                'amount': monthly_tax
            })
        
        # January to March of second year
        for month in range(1, 4):
            projection.append({
                'month': f"{month:02d}-{fy_end_year}",
                'amount': monthly_tax
            })
        
        return projection
