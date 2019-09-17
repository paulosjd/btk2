
class CalcParamIdeal:

    def __init__(self, par_name, profile, latest_val=None, latest_val2=None,
                 unit_is_default=True, con_factor=1, unit_symbol=''):
        self.profile = profile
        self.calc_method = getattr(self, par_name.replace(' ', '_').lower(), '')
        self.latest_val = latest_val
        self.latest_val2 = latest_val2
        self.required_field = ''
        self.misc_data = []
        self.unit_is_default = unit_is_default
        self.conversion_factor = con_factor
        self.unit_symbol = unit_symbol

    def get_ideal_data(self):
        if self.calc_method:
            return self.calc_method() or {}
        return {}

    def body_weight(self):
        """ Math formula assumes weight value is in kg """
        self.required_field = 'Height'
        if self.profile.height:
            ht = self.profile.height / 100
            bmi = 21.8
            if self.latest_val:
                bmi = round(
                    (self.latest_val / self.conversion_factor) / ht**2, 1
                )
                self.misc_data = [
                    f'Body mass index (BMI): {bmi} kg/m\N{SUPERSCRIPT TWO}'
                ]
            return {
                'ideal': round(2.2 * bmi + 3.5 * bmi * (ht - 1.5), 1)
            }

    def resting_heart_rate(self):
        self.required_field = 'Age'
        age = self.profile.age
        if not age:
            return
        if self.profile.age < 20:
            ideal = 60
        else:
            ideal = int(60 + (self.profile.age - 20)/2)
        return {'ideal': ideal}

    def blood_pressure(self):
        self.required_field = 'Age'
        age = self.profile.age
        if age:
            return {
                'ideal': 55.6,
                'ideal2': 34.6,
            }

    def blood_cholesterol(self):
        gender_target = 3.5
        if self.profile.gender and self.profile.gender != 'm':
            gender_target = 3.0
        self.misc_data = [f'Recommended LDL/HDL ratio: {gender_target}']
        if self.latest_val and self.latest_val2:
            try:
                ratio = round(self.latest_val2/self.latest_val, 1)
                self.misc_data.append(f'LDL/HDL ratio: {ratio}')
            except TypeError:
                pass
        return {
            'ideal': 1.6,
            'ideal2': 2.6,
            'ideal_prepend': '>',
            'ideal2_prepend': '<'
        }

    def fasting_blood_glucose(self):
        return {'ideal_prepend': '<',
                'ideal': 4.2 * self.conversion_factor}
