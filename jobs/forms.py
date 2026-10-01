"""jobs/forms.py — Job creation, editing, and preview validation form."""
from django import forms
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Job, Category


class JobForm(forms.ModelForm):
    """Form for employers to create and edit job postings."""

    status = forms.ChoiceField(
        choices=[
            (Job.Status.DRAFT, _("Save as Draft")),
            (Job.Status.OPEN, _("Publish Now")),
        ],
        widget=forms.Select(attrs={"class": "form-control"}),
        initial=Job.Status.OPEN,
        required=True,
    )
    salary_currency = forms.CharField(
        max_length=5,
        required=False,
        initial="USD",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "USD",
            "maxlength": "5",
        }),
    )

    class Meta:
        model = Job
        fields = [
            "title",
            "category",
            "job_type",
            "experience_level",
            "location",
            "is_remote",
            "salary_min",
            "salary_max",
            "salary_period",
            "salary_currency",
            "deadline",
            "description",
            "requirements",
            "responsibilities",
            "benefits",
            "status",
        ]
        widgets = {
            "title": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Senior Backend Engineer",
                "required": True,
            }),
            "category": forms.Select(attrs={"class": "form-control"}),
            "job_type": forms.Select(attrs={"class": "form-control"}),
            "experience_level": forms.Select(attrs={"class": "form-control"}),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. San Francisco, CA or Remote",
                "required": True,
            }),
            "is_remote": forms.CheckboxInput(attrs={"class": "checkbox-input"}),
            "salary_min": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Minimum (e.g. 90000)",
                "step": "1000",
            }),
            "salary_max": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "Maximum (e.g. 130000)",
                "step": "1000",
            }),
            "salary_period": forms.Select(attrs={"class": "form-control"}),
            "salary_currency": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "USD",
                "maxlength": "5",
            }),
            "deadline": forms.DateInput(attrs={
                "class": "form-control",
                "type": "date",
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": "Provide an overview of the role, team, and company mission...",
                "required": True,
            }),
            "requirements": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Required skills, years of experience, and qualifications...",
            }),
            "responsibilities": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Core day-to-day responsibilities and projects...",
            }),
            "benefits": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
                "placeholder": "Health insurance, 401(k), paid time off, remote perks...",
            }),
        }

    def __init__(self, *args, employer=None, **kwargs):
        self.employer = employer
        super().__init__(*args, **kwargs)

        self.fields["category"].empty_label = "Select Department / Category"
        self.fields["category"].queryset = Category.objects.all().order_by("name")

        # If employer is unverified, restrict the status choices
        if self.employer and not getattr(self.employer, "is_verified", True):
            self.fields["status"].choices = [
                (Job.Status.DRAFT, _("Save as Draft (Account Verification Pending)")),
            ]
            self.fields["status"].initial = Job.Status.DRAFT
            self.fields["status"].help_text = _("Unverified employers can save drafts. Once your account is verified, you can publish.")

    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")
        deadline = cleaned_data.get("deadline")
        status = cleaned_data.get("status")

        # 1. Validate salary_min <= salary_max
        if salary_min is not None and salary_max is not None:
            if salary_min > salary_max:
                self.add_error("salary_min", _("Minimum salary cannot exceed maximum salary."))
                self.add_error("salary_max", _("Maximum salary cannot be less than minimum salary."))

        # 2. Validate deadline not in the past
        if deadline:
            today = timezone.now().date()
            if deadline < today:
                self.add_error("deadline", _("Deadline cannot be in the past."))

        # 3. Unverified employers can save drafts but not publish
        if self.employer and not getattr(self.employer, "is_verified", True):
            if status == Job.Status.OPEN:
                self.add_error(
                    "status",
                    _("Unverified employers can only save drafts. Your account is pending verification."),
                )

        return cleaned_data

    def clean_salary_currency(self):
        return self.cleaned_data.get("salary_currency") or "USD"

