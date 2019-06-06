# from django import forms
# from django.core.exceptions import ValidationError
#
# from compounds.models import Activity, Bioactive, Substructure
#
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
