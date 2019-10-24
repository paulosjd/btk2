from django import forms
from django.contrib.auth.admin import UserAdmin
from django.core.exceptions import ValidationError

from app.models import Parameter, UnitOption


class ParameterAdminForm(forms.ModelForm):

    class Meta:
        model = Parameter
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_builtin'].initial = True
        self.fields['ideal_info'].required = True
        self.fields['ideal_info_url'].required = True

    def clean(self):
        cleaned_data = super(ParameterAdminForm, self).clean()
        upload_fields = cleaned_data.get('upload_fields', '')
        uf_labels = cleaned_data.get('upload_field_labels', '')
        uf_len = len(uf_labels.split(', '))
        invalid_uf_len = len(upload_fields.split(', ')) != uf_len or uf_len < 2
        if all([upload_fields, uf_labels]) and invalid_uf_len:
            raise ValidationError('upload_fields and upload_field_labels should'
                                  ' match up and upload_field_labels gt 2')
        if uf_len != cleaned_data['num_values'] + 1:
            raise ValidationError('split upload_fields_labels and '
                                  'num_values + 1 do not match up')
        return cleaned_data


class UnitOptionAdminForm(forms.ModelForm):

    class Meta:
        model = UnitOption
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_builtin'].initial = True


class CustomUserAdmin(UserAdmin):

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2',
                       'is_temporary')}
         ),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        UserAdmin.list_display = (
            'username', 'email', 'first_name', 'last_name', 'is_staff',
            'is_temporary'
        )


# class MyAdminForm(forms.ModelForm):
#
#     class Meta:
#         model = MyModel
#         fields = '__all__'
#         widgets = {
#             'notes': forms.Textarea(attrs={'rows': 3, 'cols': 60}),
#         }
