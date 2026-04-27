"""API для шаблонов характеристик."""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from catalog.services.characteristic_template import CharacteristicTemplateService
from catalog.serializers import (
    CharacteristicTemplateListSerializer, CharacteristicTemplateCreateSerializer, CharacteristicTemplateUpdateSerializer, CharacteristicTemplateDetailSerializer
)
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

logger = logging.getLogger('catalog')

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


@extend_schema(
    tags=['Каталог - Шаблоны характеристик'],
    summary='Получение списка шаблонов',
    parameters=[
        OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='group_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
    ],
    responses={200: CharacteristicTemplateListSerializer(many=True)},
    operation_id='catalog_characteristic_templates_list',
)
@extend_schema(
    tags=['Каталог - Шаблоны характеристик'],
    summary='Создание шаблона',
    request=CharacteristicTemplateCreateSerializer,
    responses={201: CharacteristicTemplateDetailSerializer, 400: {}, 403: {}},
    operation_id='catalog_characteristic_templates_create',
)
class CharacteristicTemplateView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get('search')
        group_id = request.query_params.get('group_id')
        if group_id:
            group_id = int(group_id)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        try:
            service = CharacteristicTemplateService()
            templates = service.get_list(search=search, group_id=group_id, page=page, page_size=page_size)
            return Response(CharacteristicTemplateListSerializer(templates, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Ошибка получения шаблонов: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CharacteristicTemplateCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicTemplateService()
            template = service.create(
                user=request.user,
                name=serializer.validated_data['name'],
                group_id=serializer.validated_data['group_id']
            )
            return Response(CharacteristicTemplateDetailSerializer(template).data, status=status.HTTP_201_CREATED)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка создания шаблона: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Каталог - Шаблоны характеристик'],
    summary='Получение шаблона',
    responses={200: CharacteristicTemplateDetailSerializer},
    operation_id='catalog_characteristic_templates_retrieve',
)
@extend_schema(
    tags=['Каталог - Шаблоны характеристик'],
    summary='Обновление шаблона',
    request=CharacteristicTemplateCreateSerializer,
    responses={200: CharacteristicTemplateDetailSerializer},
    operation_id='catalog_characteristic_templates_update',
)
@extend_schema(
    tags=['Каталог - Шаблоны характеристик'],
    summary='Удаление шаблона',
    responses={200: {}},
    operation_id='catalog_characteristic_templates_destroy',
)
class CharacteristicTemplateDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        try:
            service = CharacteristicTemplateService()
            return Response(CharacteristicTemplateDetailSerializer(service.get_by_id(id)).data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка получения шаблона {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: int):
        serializer = CharacteristicTemplateUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicTemplateService()
            name = serializer.validated_data.get('name')
            template = service.update(user=request.user, template_id=id, name=name)
            return Response(CharacteristicTemplateDetailSerializer(template).data, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка обновления шаблона {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id: int):
        try:
            service = CharacteristicTemplateService()
            service.delete(user=request.user, template_id=id)
            return Response({'message': 'Шаблон удалён'}, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка удаления шаблона {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)