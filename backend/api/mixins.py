import re

from rest_framework import serializers


class UsernameValidationMixin:
    def validate_username(self, value):
        print(value)
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Username should be not equal "me"'
            )
        if not re.search(r"^[\w.@+-]+", value):
            raise serializers.ValidationError(
                'Wrong format of username. Required Letters, '
                'digits and @/./+/- only.'
            )
        return value
