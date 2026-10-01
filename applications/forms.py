"""applications/forms.py — Job seeker application submission form."""
from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Application


class ApplicationForm(forms.ModelForm):
    """Job application form for applicants."""

    resume = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
            "accept": ".pdf,.doc,.docx",
        }),
        help_text=_("Upload a PDF or Word document. If omitted, your profile resume will be used."),
    )

    class Meta:
        model = Application
        fields = ["cover_letter", "resume", "portfolio_url"]
        widgets = {
            "cover_letter": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 6,
                "placeholder": _("Introduce yourself, explain your interest in this role, and highlight key experience..."),
            }),
            "portfolio_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://yourportfolio.com or https://github.com/username",
            }),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        has_profile_resume = bool(
            user and hasattr(user, "applicant_profile") and user.applicant_profile.resume
        )
        if not has_profile_resume:
            self.fields["resume"].required = True
            self.fields["resume"].help_text = _("Please upload your resume (PDF or DOCX).")
        else:
            resume_name = user.applicant_profile.resume.name.split("/")[-1]
            self.fields["resume"].required = False
            self.fields["resume"].help_text = _(
                f"Currently using profile resume: '{resume_name}'. Upload a new file here to customize for this job."
            )

    def clean_resume(self):
        from core.validators import validate_resume_file
        resume = self.cleaned_data.get("resume")
        if resume:
            validate_resume_file(resume)
        return resume

