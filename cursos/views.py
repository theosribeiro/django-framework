from rest_framework import mixins
from rest_framework import generics
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404

from rest_framework import viewsets  # API V2
from rest_framework.response import Response

from rest_framework import permissions

from .models import Curso, Avaliacao
from .serializers import CursoSerializer, AvaliacaoSerializer
from .permissions import EhSuperUser

"""
API V1
"""


class CursosAPIView(generics.ListCreateAPIView):  # GET E POST - retorna uma lista
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer


class CursoAPIView(
    generics.RetrieveUpdateDestroyAPIView):  # GET, POST, PUT E DELETE - NECESSARIO PASSAR ID - retorna 1 elemento
    queryset = Curso.objects.all()
    serializer_class = CursoSerializer


class AvaliacoesAPIView(generics.ListCreateAPIView):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer

    # sobrescrever o metodo para capturar dados necessarios (capturar todas as avaliacoes de determinado curso)
    def get_queryset(self):
        if self.kwargs.get(
                'curso_pk'):  # verificar se esta passando o id do curso na url (kwargs captura o valor do id passado)
            return self.queryset.filter(
                curso_id=self.kwargs.get('curso_pk'))  # retorna somente a avaliacao do curso selecionado
        return self.queryset.all()  # retorna todas as avaliacoes


class AvaliacaoAPIView(generics.RetrieveUpdateDestroyAPIView):  # retorna 1 elemento
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer

    # sobrescrever o metodo para capturar dados necessarios (capturar somente 1 avaliacao de determinado curso)
    def get_object(self):
        if self.kwargs.get('curso_pk'):
            return get_object_or_404(self.get_queryset(), curso_id=self.kwargs.get('curso_pk'),
                                     pk=self.kwargs.get('avaliacao_pk'))
        return get_object_or_404(self.get_queryset(), pk=self.kwargs.get('avaliacao_pk'))


"""
API V2
"""


class CursoViewSet(viewsets.ModelViewSet):
    #Permissao para cada usr acessar o curso atraves do DjangoModel (localhost:8000/admin) -> atribuir permissoes ao usr la
    permission_classes = (
        # a ordem faz a diferença
        EhSuperUser, #Se suprir essa permissao, nao vai para 'DjangoModelPermissions'
        permissions.DjangoModelPermissions,
    )

    queryset = Curso.objects.all()
    serializer_class = CursoSerializer

    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):

        self.pagination_class.page_size = 2
        avaliacoes = Avaliacao.objects.filter(curso_id=pk)
        page = self.paginate_queryset(avaliacoes)

        if page is not None:
            serializer = AvaliacaoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)


# class AvaliacaoViewSet(viewsets.ModelViewSet):
#     queryset = Avaliacao.objects.all()
#     serializer_class = AvaliacaoSerializer

class AvaliacaoViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    # mixins.DestroyModelMixin,   #comentar para nao deixar ser executado
    viewsets.GenericViewSet
):
    queryset = Avaliacao.objects.all()
    serializer_class = AvaliacaoSerializer

