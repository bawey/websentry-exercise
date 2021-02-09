import os
import pytest
from websentry.commons import AbstractConfig


class TestConfig(AbstractConfig):
    @pytest.mark.parametrize('name,value,def_val,expected', [
        ('foobar42', '0', True, False)
    ])
    def test_env_bool(self, name: str, value: str, def_val: bool, expected: bool):
        os.environ[name] = value
        assert expected == self.env_bool(name, def_val)
