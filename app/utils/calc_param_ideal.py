
class CalcParamIdeal:

    def __init__(self, param_name, profile, latest_weight=None):
        self.profile = profile
        self.calc_method = getattr(self, param_name, '')
        self.null_default = False
        self.latest_weight = latest_weight

    def get_ideal(self):
        if self.calc_method:
            return self.calc_method()

    def body_weight(self):
        # rounded all terms to one decimal place
        if not self.profile.height:
            # user note - say using default avg male, 30 175cm,
            # please enter height in profile
            self.null_default = True
            return

        ht = self.profile.height / 100
        if self.latest_weight:
            # convert to kg if in lb
            bmi = self.latest_weight / ht**2
            return 2.2 * bmi + 3.5 * bmi * (ht - 1.5)

    def blood_pressure(self):
        age = self.profile.age
