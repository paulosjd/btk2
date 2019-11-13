from django.http import HttpRequest


class BaseMockObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __len__(self):
        if hasattr(self, 'len_value'):
            return self.__dict__['len_value']
        return len(self.__dict__)


class MockObj(BaseMockObj):
    """ Usage e.g. MockObj(set_callables=[('my_mocked_method', 5), ] """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name, value in kwargs.get('callable_attrs', []):
            setattr(self, name, lambda: value)


class LazyAttrObj(BaseMockObj):
    def __getattr__(self, item):
        if not self.__dict__.get(item):
            return None


class MockRequest(HttpRequest):
    def __init__(self, method='GET', user=None):
        super().__init__()
        self.method = method
        self.user = user
