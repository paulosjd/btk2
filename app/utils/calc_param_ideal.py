
class CalcParamIdeal:

    def __init__(self, par_name, profile, latest_val=None):
        self.profile = profile
        self.calc_method = getattr(self, par_name.replace(' ', '_').lower(), '')
        self.latest_val = latest_val
        # self.latest_val2 = latest_val_2
        self.required_field = ''
        self.misc_data = []

    def get_ideal(self):
        if self.calc_method:
            return self.calc_method()

    def body_weight(self):
        """ Math formula assumes weight value is in kg """
        self.required_field = 'Height'
        if self.profile.height and self.latest_val:
            ht = self.profile.height / 100
            bmi = round(self.latest_val / ht**2, 1)
            self.misc_data = [
                f'Body mass index (BMI): {bmi} kg/m\N{SUPERSCRIPT TWO}'
            ]
            return round(2.2 * bmi + 3.5 * bmi * (ht - 1.5), 1)

    def resting_heart_rate(self):
        self.required_field = 'Age'
        age = self.profile.age
        if not age:
            return
        if self.profile.age < 20:
            return 60
        return int(60 + (self.profile.age - 20)/2)

    def blood_pressure(self):
        age = self.profile.age

    def blood_cholesterol(self):
        age = self.profile.age
        return