from rest_framework import serializers
from atomicloops.serializers import AtomicSerializer
from .models import Users, UsersDevices
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _


class UserSignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    passwordConfirm = serializers.CharField(write_only=True, min_length=8)
    age = serializers.IntegerField(required=False, allow_null=True)
    gender = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Users
        fields = ['email', 'phone', 'firstName', 'lastName', 'password', 'passwordConfirm', 'age', 'gender']

    def validate(self, data):
        if data['password'] != data.pop('passwordConfirm'):
            raise serializers.ValidationError({'password': 'Passwords do not match'})

        if not data.get('email') and not data.get('phone'):
            raise serializers.ValidationError('Either email or phone is required')

        return data

    def create(self, validated_data):
        age = validated_data.pop('age', None)
        gender = validated_data.pop('gender', None)
        
        # Default new patients: level=1 (patient), auto-verified for dev
        validated_data.setdefault('level', 1)
        user = Users.objects.create_user(**validated_data)
        user.isVerified = True
        user.save(update_fields=['isVerified'])
        
        # Update the profile automatically created by signals.py
        from profiles.models import UserProfile
        profile, created = UserProfile.objects.get_or_create(userId=user)
        profile.fullName = f"{user.firstName} {user.lastName}".strip()
        if age:
            profile.age = age
        if gender:
            profile.gender = gender[0].upper()
        profile.save()
        
        return user


class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')

        if not email and not phone:
            raise serializers.ValidationError('Email or phone is required')

        user = None
        if email:
            try:
                user = Users.objects.get(email=email)
            except Users.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')
        elif phone:
            try:
                user = Users.objects.get(phone=phone)
            except Users.DoesNotExist:
                raise serializers.ValidationError('Invalid credentials')

        if user and not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')

        data['user'] = user
        return data


class UsersSerializer(AtomicSerializer):
    class Meta:
        model = Users
        read_only_fields = ('email', 'is_superuser')
        fields = (
            'id',
            'createdAt',
            'updatedAt',
            'firstName',
            'lastName',
            'email',
            'phone',
            'level',
            'is_active',
            'is_staff',
            'is_superuser',
            'profilePicture',
            'isVerified',
        )
        get_fields = (
            'id',
            'createdAt',
            'updatedAt',
            'firstName',
            'lastName',
            'email',
            'phone',
            'level',
            'is_active',
            'is_staff',
            'is_superuser',
            'profilePicture',
            'isVerified',
        )
        list_fields = (
            'id',
            'createdAt',
            'updatedAt',
            'firstName',
            'lastName',
            'email',
            'phone',
            'level',
            'is_active',
            'profilePicture',
        )


class UserDetailSerializer(AtomicSerializer):
    class Meta:
        model = Users
        fields = ['id', 'createdAt', 'updatedAt', 'email', 'phone', 'firstName', 'lastName', 'level', 'isVerified', 'is_active']
        get_fields = ['id', 'createdAt', 'updatedAt', 'email', 'phone', 'firstName', 'lastName', 'level', 'isVerified', 'is_active']
        list_fields = ['id', 'createdAt', 'updatedAt', 'email', 'phone', 'firstName', 'lastName', 'level']
        read_only_fields = ['id', 'createdAt', 'updatedAt']


class UserUpdateSerializer(AtomicSerializer):
    class Meta:
        model = Users
        fields = ['firstName', 'lastName', 'profilePicture']
        get_fields = ['firstName', 'lastName', 'profilePicture']
        list_fields = ['firstName', 'lastName', 'profilePicture']


class UsersDevicesSerializer(AtomicSerializer):
    class Meta:
        model = UsersDevices
        fields = (
            'id',
            'createdAt',
            'updatedAt',
            'userId',
            'deviceId',
            'token',
            'deviceType',
            'info',
            'language',
        )
        get_fields = (
            'id',
            'createdAt',
            'updatedAt',
            'userId',
            'deviceId',
            'token',
            'deviceType',
            'info',
            'language',
        )
        list_fields = (
            'id',
            'deviceId',
            'deviceType',
            'language',
        )


class UpdatePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmPassword = serializers.CharField(write_only=True, required=True)
    oldPassword = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Users
        fields = ('oldPassword', 'password', 'confirmPassword')

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmPassword']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def validate_oldPassword(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"oldPassword": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):
        user = self.context['request'].user
        if user.pk != instance.pk:
            raise serializers.ValidationError({"authorize": "You dont have permission for this user."})

        instance.set_password(validated_data['password'])
        instance.save()
        return instance


class UpdateAdminStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = (
            'id',
            'is_superuser',
            'level',
        )


class UploadProfilePictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ('id', 'profilePicture')
