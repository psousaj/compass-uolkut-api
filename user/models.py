from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("O endereço de email deve ser fornecido.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    email = models.CharField(max_length=150, unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    password = models.CharField(max_length=255)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []


# Create your models here.
class Profile(models.Model):
    ESTADO_CIVIL_CHOICES = [
        ("solteiro", "Solteiro"),
        ("namorando", "Namorando"),
        ("casado", "Casado"),
        ("divorciado", "Divorciado"),
        ("preocupado", "Preocupado"),
    ]
    nome = models.CharField(max_length=100, blank=True)
    nascimento = models.DateField(default=None)
    profissao = models.CharField(max_length=100, blank=True)
    pais = models.CharField(max_length=100, default="Brasil")
    cidade = models.CharField(max_length=100, default="Juazeiro do Norte")
    estado_civil = models.CharField(
        max_length=20, choices=ESTADO_CIVIL_CHOICES, default=None
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

    def __str__(self):
        return self.nome
