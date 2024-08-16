from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.db import transaction

from users.models import Profile

User = get_user_model()


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['telegram_id', 'photo']


class UserProfileForm(forms.Form):
    telegram_id = forms.CharField(max_length=30, required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        user_instance = kwargs.pop('instance', None)
        profile_instance = getattr(user_instance, 'profile', None)

        super().__init__(*args, **kwargs)

        self.user = UserForm(
            instance=user_instance,
            data=self.data or None
        )
        self.profile = ProfileForm(
            instance=profile_instance,
            data=self.data or None,
            files=self.request.FILES if self.request else None
        )

        if profile_instance:
            # в методе __init__ переменная self.profile содержит telegram_id, который, однако, в процессе рендеринга формы теряется..
            self.fields['telegram_id'].initial = profile_instance.telegram_id

    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     user_instance = kwargs.pop('instance', None)
    #     profile_instance = getattr(user_instance, 'profile', None)
    #
    #     super().__init__(*args, **kwargs)
    #
    #     self.user = UserForm(
    #         instance=user_instance,
    #         data=self.data or None
    #     )
    #     self.profile = ProfileForm(
    #         instance=profile_instance,
    #         data=self.data or None,
    #         files=self.request.FILES if self.request else None
    #     )
    #
    #     print(f"User instance: {user_instance}")
    #     print(f"Profile instance: {profile_instance}")
    #     if profile_instance:
    #         self.fields['telegram_id'].initial = profile_instance.telegram_id
    #         print(f"Telegram ID: {profile_instance.telegram_id}")
    #         print(f"Photo: {profile_instance.photo}")
    #     print(f"Profile form initial data: {self.profile.initial}")
    #     print(f"Profile form initial data: {self.user.last_name}")

    def is_valid(self):
        return self.user.is_valid() and self.profile.is_valid()

    def save(self, commit=True):
        with transaction.atomic():
            user = self.user.save(commit=commit)
            profile = self.profile.save(commit=False)
            profile.user = user
            if commit:
                profile.save()
        return user


class CreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('first_name', 'last_name', 'username', 'user_group', 'email', 'phone_number')

    user_group = forms.ChoiceField(choices=User.group_choices, widget=forms.RadioSelect())

    @transaction.atomic
    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            phone_number=self.cleaned_data['phone_number']
        )

        group_name = self.cleaned_data['user_group']
        user_group = Group.objects.get(name=group_name)
        user.groups.add(user_group)

        if commit:
            user.save()

        return user
