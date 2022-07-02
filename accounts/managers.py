from django.contrib.auth.models import BaseUserManager


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, operator_id, password, **extra_fields):

        """Create and save a User with the given phone and password."""

        if not operator_id:
            raise ValueError('The given phone must be set')
        self.phone = operator_id
        user = self.model(operator_id=operator_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, operator_id, password):
        if not operator_id:
            raise ValueError('Operator_id must be set')

        user = self.model(operator_id=operator_id)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, operator_id, password, **extra_fields):

        """Create and save a SuperUser with the given phone and password."""

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(operator_id, password, **extra_fields)

