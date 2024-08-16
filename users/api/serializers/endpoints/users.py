from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ParseError

from users.api.serializers.mixins import ProfileSerializerMixin, ProfileShortSerializer, ProfileExtendedSerializerMixin

User = get_user_model()


class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    user_group = serializers.ChoiceField(choices=User.group_choices, write_only=True)

    class Meta:
        model = User
        fields = (
            'username',
            'password',
            'password_confirm',
            'email',
            'user_group'
        )

    def validate_email(self, value):
        email = value.lower()
        if User.objects.filter(email=email).exists():
            raise ParseError('This email is already in use.')
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        new_pass = attrs.get('password')
        new_pass_confirm = attrs.pop('password_confirm')

        if new_pass != new_pass_confirm:
            raise ParseError('Passwords don\'t match.')

        return attrs

    def create(self, validated_data):
        group_name = validated_data.pop('user_group')
        with transaction.atomic():
            user = User.objects.create_user(**validated_data)
            user.set_password(validated_data['password'])
            user.save()
            user_group = Group.objects.get(name=group_name)
            user.groups.add(user_group)
        return user


class ChangePasswordSerializer(serializers.ModelSerializer):
    old_pass = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
    )
    new_pass = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password],
    )
    new_pass_confirm = serializers.CharField(
        style={'input_type': 'password'},
        write_only=True,
        validators=[validate_password],
    )

    class Meta:
        model = User
        fields = (
            'old_pass',
            'new_pass',
            'new_pass_confirm',
        )

    def validate(self, attrs):
        user = self.instance
        old_pass = attrs.pop('old_pass')
        new_pass = attrs.get('new_pass')
        new_pass_confirm = attrs.pop('new_pass_confirm')
        if not user.check_password(old_pass):
            raise ParseError('Old password is not correct')

        if new_pass != new_pass_confirm:
            raise ParseError('New password is not correct')

        return attrs

    def update(self, instance, validated_data):
        new_password = validated_data.pop('new_pass')
        instance.set_password(new_password)
        instance.save()
        return instance


class MeSerializer(ProfileSerializerMixin):
    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile') if 'profile' in validated_data else None
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if profile_data:
                profile_serializer = ProfileShortSerializer(
                    instance=instance.profile,
                    data=profile_data,
                    partial=True
                )
                profile_serializer.is_valid(raise_exception=True)
                profile_serializer.save()

        return instance


class FullMeSerializer(ProfileExtendedSerializerMixin):
    ...


class UserProfileSerializer(ProfileSerializerMixin):
    subscribed = serializers.BooleanField(source='user_subscribed')

    class Meta(ProfileSerializerMixin.Meta):
        fields = ProfileSerializerMixin.Meta.fields + ('subscribed',)


class FullUserProfileSerializer(ProfileExtendedSerializerMixin):
    subscribed = serializers.BooleanField(source='user_subscribed')

    class Meta(ProfileExtendedSerializerMixin.Meta):
        fields = ProfileExtendedSerializerMixin.Meta.fields + ('subscribed',)

    def get_fields(self):
        """
        Reorders the 'posts' and 'comments' fields to come after 'subscribed'.
        """
        fields = super().get_fields()
        fields['subscribed'] = fields.pop('subscribed')
        fields['posts'] = fields.pop('posts')
        fields['comments'] = fields.pop('comments')
        return fields
