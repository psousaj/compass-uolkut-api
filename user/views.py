from rest_framework import generics, permissions, viewsets
from rest_framework.response import Response

from user.models import CustomUser, Profile
from user.serializer import CustomUserSerializer, ProfileSerializer


def validate_user_already_exists(email):
    user = CustomUser.objects.filter(email=email)
    if user.exists():
        return user.first()

    return None


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
        if not user_id:
            raise Exception("Informe o id usuario!")
        try:
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
        email = request.data.get("email")
        user = validate_user_already_exists(email)
        if not user:
            try:
                user = CustomUser.objects.create_user(
                    email=email, password=request.data.get("password")
                )
                user.save()
            except ValueError as e:
                return Response({"message": "Algo deu errado! :(", "error": str(e)})

        # Crie um dicionário com os dados a serem passados para o serializador
        data_to_serialize = {
            "nome": request.data.get("nome"),
            "nascimento": request.data.get("nascimento"),
            "profissao": request.data.get("profissao"),
            "pais": request.data.get("pais"),
            "cidade": request.data.get("cidade"),
            "estado_civil": request.data.get("estado_civil"),
            "user": user.id,
        }

        serializer = self.get_serializer(data=data_to_serialize)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
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
