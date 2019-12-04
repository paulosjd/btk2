from django.http import HttpRequest


class MockObj:
    """ Usage e.g. MockObj(color='red', set_callables=[('my_method', 5), ]) """
    def __init__(self, **kwargs):
        for name, value in kwargs.pop('callable_attrs', []):
            setattr(self, name, lambda: value)
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __len__(self):
        if hasattr(self, 'len_value'):
            return self.len_value
        return len(self.__dict__)


class MockCeleryAsyncResult:
    def __init__(self, should_be_ready=False):
        self.should_be_ready = should_be_ready
        self.ready = lambda: self.should_be_ready
        self.result = 'result'

    @classmethod
    def create_ready(cls, task_id):
        return cls(should_be_ready=True)

    @classmethod
    def create_not_ready(cls, task_id):
        return cls(should_be_ready=False)


class LazyAttrObj(MockObj):
    def __getattr__(self, item):
        if not self.__dict__.get(item):
            return None


class MockRequest(HttpRequest):
    def __init__(self, method='GET', data=None, user=None):
        super().__init__()
        self.method = method
        self.user = user
        self.data = data or {}


class MockOpenFileNotFound:
    def __init__(self, *args):
        pass

    def __enter__(self):
        raise FileNotFoundError

    def __exit__(self, *args):
        pass
