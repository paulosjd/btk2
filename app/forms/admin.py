from django import forms
from django.core.exceptions import ValidationError

from app.models import Parameter


class ParameterAdminForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = '__all__'

    def clean(self):
        cleaned_data = super(ParameterAdminForm, self).clean()
        upload_fields = cleaned_data.get('upload_fields')
        upload_field_labels = cleaned_data.get('upload_field_labels')
        if all([upload_fields, upload_field_labels]) and \
                len(upload_fields.split(', ')) != len(upload_field_labels.split(', ')):
            raise ValidationError('upload_fields and upload_field_labels should match up')
        return cleaned_data



#
# class ActivityAdminForm(forms.ModelForm):
#     class Meta:
#         model = Activity
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super(ActivityAdminForm, self).__init__(*args, **kwargs)
#         self.fields['action'].queryset = Activity.objects.actions()
#
#     def clean(self):
#         cleaned_data = super(ActivityAdminForm, self).clean()
#         category = cleaned_data.get('category')
#         if category == 2 and not cleaned_data.get('action'):
#             raise ValidationError('Action reference required for the mechanism')
#         if category != 2 and cleaned_data.get('action'):
#             raise ValidationError('Action reference only allowed if category is mechanism')
#         return cleaned_data
#
#
# class SubstructureAdminForm(forms.ModelForm):
#
#     class Meta:
#         model = Substructure
#         fields = '__all__'
#         widgets = {
#             'description': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
#         }
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['iupac_name_pattern'].delimiter = '|'
#         self.fields['iupac_name_pattern'].help_text = 'Substring patterns delimited by |'
#         self.fields['smiles'].required = True
#
#
# class BioactiveAdminForm(forms.ModelForm):
#
#     class Meta:
#         model = Bioactive
#         fields = '__all__'
#         widgets = {
#             'notes': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
#         }
