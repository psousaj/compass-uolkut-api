from django.db import IntegrityError
from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from user.models import CustomUser, Profile
from user.serializer import CustomUserSerializer, ProfileSerializer


def validate_user_already_exists(email):
    user = CustomUser.objects.filter(email=email)
    if user.exists():
        return user.first()

    return False


# Create your views here.
class UserView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            if not email:
                raise Exception("Informe o email!")
        except Exception as e:
            return Response(
                {"message": "Usuário inválido", "error": f"{str(e)}"}, status=400
            )

        serializer = self.serializer_class(request.data)
        return Response(serializer.data, status=201)

    def put(self, request):
        user_id = request.query_params.get("id")
        try:
            if not user_id:
                raise Exception("Informe o id usuario!")
            user = CustomUser.objects.get(id=user_id)
        except Exception as e:
            return Response(
                {"message": "Usuário inválido", "error": f"{str(e)}"}, status=400
            )

        # Verificar se o usuário está atualizando seu próprio perfil
        if user.id != request.user.id:
            return Response(
                {"message": "You are not authorized to update this profile."},
                status=403,
            )

        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        user_id = request.query_params.get("id")

        try:
            if user_id:
                user = CustomUser.objects.get(id=user_id)
            else:
                user = CustomUser.objects.get(id=request.user.id)
        except Exception as e:
            return Response(
                {"message": "Usuário inválido", "error": f"{str(e)}"}, status=400
            )

        # Verificar se o usuário está atualizando seu próprio perfil
        if user.id != request.user.id:
            return Response(
                {"message": "You are not authorized to update this profile."},
                status=403,
            )

        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


class ProfileView(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        queryset = Profile.objects.all()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(
                nome__icontains=name
            )  # Filtra nomes que contenham o valor de 'name'

        if queryset.count() == 0:
            raise ValueError("Nenhum perfil encontrado!")

        return queryset

    def listUser(self, request, *args, **kwargs):
        try:
            queryset = Profile.objects.get(user=request.user.id)
        except ValueError as e:
            return Response(
                {"message": "Algo deu errado! :(", "error": str(e)}, status=200
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
        except ValueError as e:
            return Response(
                {"message": "Algo deu errado! :(", "error": str(e)}, status=200
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get("email")
            password = request.data.get("password")  # Recupere a senha do request
            user, created = CustomUser.objects.get_or_create(email=email)

            if created:
                user.set_password(password)  # Defina a senha para o novo usuário
                user.save()  # Salve o usuário com a senha

            # Crie um dicionário com os dados a serem passados para o serializador
            data_to_serialize = {
                "name": request.data.get("name"),
                "birth": request.data.get("birth"),
                "profession": request.data.get("profissao"),
                "country": request.data.get("country"),
                "city": request.data.get("city"),
                "relationship": request.data.get("relationship"),
            }

            serializer = self.get_serializer(data=data_to_serialize)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            # Associe o perfil ao usuário usando o método set_user_profile
            profile_instance = serializer.instance
            profile_instance.set_user_profile(user)
        except IntegrityError as e:
            return Response(
                {
                    "message": "Algo deu errado! :(",
                    "hint": "Esse usuario já tem um perfil atrelado a ele! Use outro email",
                    "error": f"{str(e)}",
                }
            )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def patch(self, request):
        user_id = request.query_params.get("id")

        try:
            if user_id:
                user = CustomUser.objects.get(id=user_id)
            else:
                user = CustomUser.objects.get(id=request.user.id)
            profile = Profile.objects.get(user=user.id)
        except Exception as e:
            return Response(
                {"message": "Usuário inválido", "error": f"{str(e)}"}, status=400
            )

        # instance = self.get_object()
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=200)
