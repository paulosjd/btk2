from django.http import HttpRequest


class BaseMockObj:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __len__(self):
        if hasattr(self, 'len_value'):
            return self.len_value
        return len(self.__dict__)


class MockObj(BaseMockObj):
    """ Usage e.g. MockObj(set_callables=[('my_mocked_method', 5), ] """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        for name, value in kwargs.get('callable_attrs', []):
            setattr(self, name, lambda: value)


# TODO Make a class factory so that can return MockObj whereby
# e.g. foo = AsyncCeleryResult(task_id)  .. foo.ready()  ->
# mock_obj instance created by AsyncCeleryResult patch is True of False
# is True or False depending on args to factory call
# so no need to do inheritance where one implementation returns True other False


class LazyAttrObj(BaseMockObj):
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
