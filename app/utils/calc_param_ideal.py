
class CalcParamIdeal:

    def __init__(self, par_name, profile, latest_val=None):
        self.profile = profile
        self.calc_method = getattr(self, par_name.replace(' ', '_').lower(), '')
        self.latest_val = latest_val
        # self.latest_val2 = latest_val_2
        self.misc_data = []

    def get_ideal(self):
        if self.calc_method:
            return self.calc_method()

    def body_weight(self):
        """ Math formula assumes weight value is in kg """
        if self.profile.height and self.latest_val:
            ht = self.profile.height / 100
            bmi = round(self.latest_val / ht**2, 1)
            self.misc_data = [
                f'Body mass index (BMI): {bmi} kg/m\N{SUPERSCRIPT TWO}'
            ]
            return round(2.2 * bmi + 3.5 * bmi * (ht - 1.5), 1)

    def blood_pressure(self):
        age = self.profile.age
