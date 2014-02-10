from django.utils import timezone
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from flavor import Flavor
from providers import Provider


@receiver(pre_save, sender=User, dispatch_uid='api.models')
def user_pre_save_handler(**kwargs):
    """Replicate UserManager.create_user functionality."""

    user = kwargs['instance']

    now = timezone.now()
    user.last_login = now
    user.date_joined = now
    user.is_active = True
    user.email = User.objects.normalize_email(user.email)
    user.set_password(user.password)
    # Make this first signup an admin / superuser
    if not User.objects.filter(is_superuser=True).exists():
        user.is_superuser = user.is_staff = True


@receiver(post_save, sender=User, dispatch_uid='api.models')
def user_post_save_handler(**kwargs):
    """Callbacks for when a user is first created."""

    user = kwargs['instance']

    # Seed both `Providers` and `Flavors` after registration.
    if kwargs['created']:
        Provider.objects.seed(user)
        Flavor.objects.seed(user)

    # Publish user to Config Manager
    if kwargs.get('update_fields') != frozenset(['last_login']):
        user.publish()


@receiver(post_delete, sender=User, dispatch_uid='api.models')
def _purge_user_from_cm(**kwargs):
    kwargs['instance'].purge()
