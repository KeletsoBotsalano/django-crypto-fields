import sys

from Crypto.Cipher import AES
from django.apps import apps as django_apps
from django.apps import AppConfig as DjangoAppConfig
from django.core.management.color import color_style
from django_crypto_fields.cryptor import Cryptor


class DjangoCryptoFieldsError(Exception):
    pass


style = color_style()


class AppConfig(DjangoAppConfig):
    name = 'django_crypto_fields'
    verbose_name = "Data Encryption"
    encryption_keys = None
    app_label = 'django_crypto_fields'
    # change if using more than one database and not 'default'.
    crypt_model_using = 'default'

    def __init__(self, app_label, model_name):
        """Placed here instead of `ready()`. For models to load correctly that use
        field classes from this module the keys need to be loaded before models."""
        super(AppConfig, self).__init__(app_label, model_name)
        from django_crypto_fields.keys import Keys
        keys = Keys()
        if not self.encryption_keys:
            sys.stdout.write('Loading {} ...\n'.format(self.verbose_name))
            if not keys.key_files_exist():
                sys.stdout.write(style.NOTICE('Warning: {} failed to load encryption keys.\n'.format(
                    self.verbose_name)))
                sys.stdout.write(
                    'Confirm that settings.KEY_PATH points to the correct folder.\n')
                sys.stdout.write(
                    'Loading the wrong encryption keys can corrupt sensitive data.\n')
                sys.stdout.write('If this is your first time loading the project, '
                                 'new keys will be generated\n')
                sys.stdout.write(
                    'and placed in the settings.KEY_PATH folder.\n')
                keys.create_keys()
            keys.load_keys()
            self.encryption_keys = keys
            sys.stdout.write(
                ' * using model {}.{}.\n'.format(self.app_label, 'crypt'))
            sys.stdout.write(' Done loading {}.\n'.format(self.verbose_name))
            sys.stdout.flush()

    def ready(self):
        cryptor = Cryptor()
        if cryptor.aes_encryption_mode == AES.MODE_CFB:
            sys.stdout.write(style.NOTICE(
                'Warning: Encryption mode MODE_CFB should not be used. \n'
                '         See django_crypto_fields.cryptor.py and comments \n'
                '         in pycrypto.blockalgo.py.\n'))
            sys.stdout.flush()

    @property
    def model(self):
        return django_apps.get_model(self.app_label, 'crypt')
