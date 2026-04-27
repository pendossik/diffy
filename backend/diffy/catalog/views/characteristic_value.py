"""API для значений характеристик."""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
import logging

from catalog.services.characteristic_value import CharacteristicValueService
from catalog.serializers import (
    CharacteristicValueListSerializer, CharacteristicValueCreateSerializer, CharacteristicValueUpdateSerializer, CharacteristicValueDetailSerializer
)
from catalog.services.exceptions import PermissionDeniedError
from catalog.validators.exceptions import ValidationError, ObjectNotFoundError as CatalogObjectNotFoundError
from infrastructure.exceptions import ObjectNotFoundError as InfrastructureObjectNotFoundError

logger = logging.getLogger('catalog')

ObjectNotFoundError = (CatalogObjectNotFoundError, InfrastructureObjectNotFoundError)


@extend_schema(
    tags=['Каталог - Значения характеристик'],
    summary='Получение списка значений',
    parameters=[
        OpenApiParameter(name='search', type=OpenApiTypes.STR, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='product_id', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
        OpenApiParameter(name='page_size', type=OpenApiTypes.INT, location=OpenApiParameter.QUERY, required=False),
    ],
    responses={200: CharacteristicValueListSerializer(many=True)},
    operation_id='catalog_characteristic_values_list',
)
@extend_schema(
    tags=['Каталог - Значения характеристик'],
    summary='Создание значения',
    request=CharacteristicValueCreateSerializer,
    responses={201: CharacteristicValueDetailSerializer, 400: {}, 403: {}},
    operation_id='catalog_characteristic_values_create',
)
class CharacteristicValueView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        search = request.query_params.get('search')
        product_id = request.query_params.get('product_id')
        if product_id:
            product_id = int(product_id)
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))
        try:
            service = CharacteristicValueService()
            values = service.get_list(search=search, product_id=product_id, page=page, page_size=page_size)
            return Response(CharacteristicValueListSerializer(values, many=True).data, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Ошибка получения значений: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        serializer = CharacteristicValueCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicValueService()
            value = service.create(
                user=request.user,
                product_id=serializer.validated_data['product_id'],
                template_id=serializer.validated_data['template_id'],
                value=serializer.validated_data['value']
            )
            return Response(CharacteristicValueDetailSerializer(value).data, status=status.HTTP_201_CREATED)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка создания значения: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@extend_schema(
    tags=['Каталог - Значения характеристик'],
    summary='Получение значения',
    responses={200: CharacteristicValueDetailSerializer},
    operation_id='catalog_characteristic_values_retrieve',
)
@extend_schema(
    tags=['Каталог - Значения характеристик'],
    summary='Обновление значения',
    request=CharacteristicValueCreateSerializer,
    responses={200: CharacteristicValueDetailSerializer},
    operation_id='catalog_characteristic_values_update',
)
@extend_schema(
    tags=['Каталог - Значения характеристик'],
    summary='Удаление значения',
    responses={200: {}},
    operation_id='catalog_characteristic_values_destroy',
)
class CharacteristicValueDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        try:
            service = CharacteristicValueService()
            return Response(CharacteristicValueDetailSerializer(service.get_by_id(id)).data, status=status.HTTP_200_OK)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка получения значения {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, id: int):
        serializer = CharacteristicValueUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'error': 'Ошибка валидации'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            service = CharacteristicValueService()
            value = service.update(user=request.user, value_id=id, value=serializer.validated_data.get('value'))
            return Response(CharacteristicValueDetailSerializer(value).data, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except ValidationError as e:
            return Response({'error': e.message}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Ошибка обновления значения {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, id: int):
        try:
            service = CharacteristicValueService()
            service.delete(user=request.user, value_id=id)
            return Response({'message': 'Значение удалено'}, status=status.HTTP_200_OK)
        except PermissionDeniedError as e:
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ObjectNotFoundError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Ошибка удаления значения {id}: {e}")
            return Response({'error': 'Внутренняя ошибка сервера'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)