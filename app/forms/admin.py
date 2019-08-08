from django import forms
from django.core.exceptions import ValidationError

from app.models import Parameter, User


class ParameterAdminForm(forms.ModelForm):
    class Meta:
        model = Parameter
        fields = '__all__'

    def clean(self):
        cleaned_data = super(ParameterAdminForm, self).clean()
        upload_fields = cleaned_data.get('upload_fields')
        uf_labels = cleaned_data.get('upload_field_labels', '')
        uf_len = len(uf_labels.split(', '))
        invalid_uf_len = len(upload_fields.split(', ')) != uf_len or uf_len < 2
        if all([upload_fields, uf_labels]) and invalid_uf_len:
            raise ValidationError('upload_fields and uplaod_field_labels should'
                                  ' match up and upload_field_labels gt 2')
        if uf_len != cleaned_data['num_values'] + 1:
            raise ValidationError('split upload_fields_labels and '
                                  'num_values + 1 do not match up')
        return cleaned_data


# class UserCreationForm(forms.ModelForm):
#     password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
#     password2 = forms.CharField(label='Password confirmation',
#                                 widget=forms.PasswordInput)
#     is_temporary = forms.BooleanField(label='Is temp user')
#
#     class Meta:
#         model = User
#         fields = '__all__'
#
#     def clean_password2(self):
#         password1 = self.cleaned_data.get("password1")
#         password2 = self.cleaned_data.get("password2")
#         if password1 and password2 and password1 != password2:
#             raise forms.ValidationError("Passwords don't match")
#         return password2
#
#     def save(self, commit=True):
#         user = super().save(commit=False)
#         user.set_password(self.cleaned_data["password1"])
#         if commit:
#             user.save()
#         return user


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
