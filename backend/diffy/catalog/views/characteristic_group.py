"""API для групп характеристик."""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from catalog.services.characteristic_group import CharacteristicGroupService
from catalog.serializers import (
    CharacteristicGroupListSerializer, CharacteristicGroupCreateSerializer, CharacteristicGroupUpdateSerializer, CharacteristicGroupDetailSerializer
)
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

logger = logging.getLogger('catalog')

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


@extend_schema(
    tags=['Каталог - Группы характеристик'],
    summary='Получение списка групп',
    parameters=[
        OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='category_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
    ],
    responses={200: CharacteristicGroupListSerializer(many=True)},
    operation_id='catalog_characteristic_groups_list',
)
@extend_schema(
    tags=['Каталог - Группы характеристик'],
    summary='Создание группы',
    request=CharacteristicGroupCreateSerializer,
    responses={201: CharacteristicGroupDetailSerializer, 400: {}, 403: {}},
    operation_id='catalog_characteristic_groups_create',
)
class CharacteristicGroupView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get('search')
        category_id = request.query_params.get('category_id')
        if category_id:
            category_id = int(category_id)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        try:
            service = CharacteristicGroupService()
            groups = service.get_list(search=search, category_id=category_id, page=page, page_size=page_size)
            return Response(CharacteristicGroupListSerializer(groups, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Ошибка получения групп: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CharacteristicGroupCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicGroupService()
            group = service.create(
                user=request.user,
                name=serializer.validated_data['name'],
                category_id=serializer.validated_data['category_id']
            )
            return Response(CharacteristicGroupDetailSerializer(group).data, status=status.HTTP_201_CREATED)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка создания группы: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Каталог - Группы характеристик'],
    summary='Получение группы',
    responses={200: CharacteristicGroupDetailSerializer},
    operation_id='catalog_characteristic_groups_retrieve',
)
@extend_schema(
    tags=['Каталог - Группы характеристик'],
    summary='Обновление группы',
    request=CharacteristicGroupCreateSerializer,
    responses={200: CharacteristicGroupDetailSerializer},
    operation_id='catalog_characteristic_groups_update',
)
@extend_schema(
    tags=['Каталог - Группы характеристик'],
    summary='Удаление группы',
    responses={200: {}},
    operation_id='catalog_characteristic_groups_destroy',
)
class CharacteristicGroupDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        try:
            service = CharacteristicGroupService()
            return Response(CharacteristicGroupDetailSerializer(service.get_by_id(id)).data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка получения группы {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: int):
        serializer = CharacteristicGroupUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicGroupService()
            name = serializer.validated_data.get('name')
            group = service.update(user=request.user, group_id=id, name=name)
            return Response(CharacteristicGroupDetailSerializer(group).data, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка обновления группы {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id: int):
        try:
            service = CharacteristicGroupService()
            service.delete(user=request.user, group_id=id)
            return Response({'message': 'Группа удалена'}, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка удаления группы {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)