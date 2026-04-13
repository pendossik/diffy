"""API-представления приложения characteristic."""
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
import logging
from .services import (
    CharacteristicGroupService,
    CharacteristicTemplateService,
    CharacteristicValueService,
)
from .serializers import (
    CharacteristicGroupListSerializer, CharacteristicGroupDetailSerializer,
    CharacteristicGroupCreateSerializer, CharacteristicGroupUpdateSerializer,
    CharacteristicTemplateListSerializer, CharacteristicTemplateDetailSerializer,
    CharacteristicTemplateCreateSerializer, CharacteristicTemplateUpdateSerializer,
    CharacteristicValueListSerializer, CharacteristicValueDetailSerializer,
    CharacteristicValueCreateSerializer, CharacteristicValueUpdateSerializer,
)
from categories.serializers import CategoryDetailSerializer

logger = logging.getLogger('characteristic')


# =============================================================================
# CategoryCharacteristicsGroupsView — публичный список групп для категории
# =============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=['Характеристики категории'],
        summary='Получение списка групп характеристик категории',
        description=(
            'Получить все группы характеристик для указанной категории с вложенными шаблонами.\n\n'
            '**Возвращает:**\n'
            '- `id` — уникальный идентификатор группы\n'
            '- `name` — название на текущем языке запроса\n'
            '- `name_ru` — название на русском языке\n'
            '- `name_en` — название на английском языке\n'
            '- `category` — ID категории\n'
            '- `category_info` — информация о категории\n'
            '- `order` — порядок сортировки\n'
            '- `templates` — список шаблонов характеристик в группе\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/categories/1/characteristics-groups/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор категории',
                examples=[OpenApiExample('ID категории', value=1)],
            ),
        ],
        responses={
            200: CharacteristicGroupDetailSerializer(many=True),
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Категория не найдена'}}},
        },
        operation_id='category_characteristics_groups',
    ),
)
class CategoryCharacteristicsGroupsView(APIView):
    """
    REST API эндпоинт для получения списка групп характеристик категории.

    **GET** — получение списка групп (доступно всем).
    """
    permission_classes = [AllowAny]

    def get(self, request, id: int):
        """Получить все группы характеристик для категории."""
        from categories.services import CategoryService
        try:
            CategoryService.get_category_detail(id)
        except ValueError:
            return Response({'error': 'Категория не найдена'}, status=status.HTTP_404_NOT_FOUND)

        try:
            groups = CharacteristicGroupService.get_groups_by_category(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CharacteristicGroupDetailSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# CharacteristicGroup Views
# =============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=['Группы характеристик'],
        summary='Получение списка групп характеристик',
        description=(
            'Получить список всех групп характеристик.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/characteristic/groups/\n'
            '```'
        ),
        responses={
            200: CharacteristicGroupListSerializer(many=True),
        },
        operation_id='characteristic_groups_list',
    ),
    post=extend_schema(
        tags=['Группы характеристик'],
        summary='Создание новой группы характеристик',
        description=(
            'Создать новую группу характеристик для категории.\n\n'
            '**Требования:**\n'
            '- Только для администраторов (`role: admin` или `superuser`)\n'
            '- Название должно быть уникальным в рамках категории\n'
            '- Категория должна существовать\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/characteristic/characteristic/groups/\n'
            '{\n'
            '  "name": "Основные параметры",\n'
            '  "name_ru": "Основные параметры",\n'
            '  "name_en": "Basic Specs",\n'
            '  "category": 1,\n'
            '  "order": 1\n'
            '}\n'
            '```'
        ),
        request=CharacteristicGroupCreateSerializer,
        responses={
            201: CharacteristicGroupDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут создавать группы характеристик'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Группа с таким именем уже существует в этой категории'}}},
        },
        operation_id='characteristic_groups_create',
    ),
)
class CharacteristicGroupListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком групп характеристик.

    **GET** — получение списка групп (доступно всем).
    **POST** — создание новой группы (только для администраторов).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        """Получить список всех групп характеристик."""
        try:
            from django.db.models import Prefetch
            from .models import CharacteristicTemplate
            groups = CharacteristicGroupService.get_groups_by_category.__self__  # fallback
            # Получаем все группы напрямую
            from .models import CharacteristicGroup
            groups = CharacteristicGroup.objects.all().select_related('category').prefetch_related(
                Prefetch('templates', queryset=CharacteristicTemplate.objects.order_by('order'))
            ).order_by('category', 'order')
        except Exception:
            from .models import CharacteristicGroup
            groups = CharacteristicGroup.objects.all().select_related('category').order_by('category', 'order')

        serializer = CharacteristicGroupListSerializer(groups, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Создать новую группу характеристик."""
        serializer = CharacteristicGroupCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                category_id = serializer.validated_data['category']
                group = CharacteristicGroupService.create_group(
                    user=request.user,
                    category_id=category_id,
                    name=serializer.validated_data['name'],
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en'),
                    order=serializer.validated_data.get('order', 0)
                )
                logger.info(f"Группа характеристик создана: '{group.name}' (пользователь: {request.user.email})")
                from django.urls import reverse
                headers = {'Location': reverse('characteristic-group-detail', args=[group.pk])}
                return Response(
                    CharacteristicGroupDetailSerializer(group).data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            except PermissionError as e:
                logger.warning(f"Попытка создания группы без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Группы характеристик'],
        summary='Получение детальной информации о группе характеристик',
        description=(
            'Получить полную информацию о группе характеристик по её идентификатору.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/characteristic/groups/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор группы',
                examples=[OpenApiExample('ID группы', value=1)],
            ),
        ],
        responses={
            200: CharacteristicGroupDetailSerializer,
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Группа характеристик не найдена'}}},
        },
        operation_id='characteristic_groups_retrieve',
    ),
    put=extend_schema(
        tags=['Группы характеристик'],
        summary='Обновление группы характеристик',
        description=(
            'Обновить данные группы характеристик.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PUT /api/characteristic/characteristic/groups/1/\n'
            '{\n'
            '  "name": "Обновлённая группа",\n'
            '  "name_ru": "Обновлённая группа",\n'
            '  "name_en": "Updated Group",\n'
            '  "order": 10\n'
            '}\n'
            '```'
        ),
        request=CharacteristicGroupUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор группы',
                examples=[OpenApiExample('ID группы', value=1)],
            ),
        ],
        responses={
            200: CharacteristicGroupDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять группы характеристик'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Группа характеристик не найдена'}}},
        },
        operation_id='characteristic_groups_update',
    ),
    delete=extend_schema(
        tags=['Группы характеристик'],
        summary='Удаление группы характеристик',
        description=(
            'Безвозвратно удалить группу характеристик.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример:**\n'
            '```\n'
            'DELETE /api/characteristic/characteristic/groups/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор группы',
                examples=[OpenApiExample('ID группы', value=1)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Группа характеристик успешно удалена'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут удалять группы характеристик'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Группа характеристик не найдена'}}},
        },
        operation_id='characteristic_groups_destroy',
    ),
)
class CharacteristicGroupDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельной группой характеристик.

    **GET** — получение детальной информации (доступно всем).
    **PUT** — обновление группы (только администраторы).
    **DELETE** — удаление группы (только администраторы).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk: int):
        """Получить детальную информацию о группе характеристик."""
        try:
            group = CharacteristicGroupService.get_group_detail(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CharacteristicGroupDetailSerializer(group)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        """Обновить группу характеристик."""
        serializer = CharacteristicGroupUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group = CharacteristicGroupService.get_group_detail(pk)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

            try:
                group = CharacteristicGroupService.update_group(
                    user=request.user,
                    group_id=pk,
                    name=serializer.validated_data.get('name'),
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en'),
                    order=serializer.validated_data.get('order')
                )
                logger.info(f"Группа характеристик обновлена: ID={pk} (пользователь: {request.user.email})")
                return Response(
                    CharacteristicGroupDetailSerializer(group).data,
                    status=status.HTTP_200_OK
                )
            except PermissionError as e:
                logger.warning(f"Попытка изменения группы без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk: int):
        """Удалить группу характеристик."""
        try:
            CharacteristicGroupService.delete_group(
                user=request.user,
                group_id=pk
            )
            logger.info(f"Группа характеристик удалена: ID={pk} (пользователь: {request.user.email})")
            return Response(
                {'message': 'Группа характеристик успешно удалена'},
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка удаления группы без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# CharacteristicTemplate Views
# =============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=['Шаблоны характеристик'],
        summary='Получение списка шаблонов характеристик',
        description=(
            'Получить список всех шаблонов характеристик.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/characteristic/templates/\n'
            '```'
        ),
        responses={
            200: CharacteristicTemplateListSerializer(many=True),
        },
        operation_id='characteristic_templates_list',
    ),
    post=extend_schema(
        tags=['Шаблоны характеристик'],
        summary='Создание нового шаблона характеристики',
        description=(
            'Создать новый шаблон характеристики для группы.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n'
            '- Название должно быть уникальным в рамках группы\n'
            '- Группа должна существовать\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/characteristic/characteristic/templates/\n'
            '{\n'
            '  "name": "Вес",\n'
            '  "name_ru": "Вес",\n'
            '  "name_en": "Weight",\n'
            '  "group": 1,\n'
            '  "order": 1\n'
            '}\n'
            '```'
        ),
        request=CharacteristicTemplateCreateSerializer,
        responses={
            201: CharacteristicTemplateDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут создавать шаблоны характеристик'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Шаблон с таким именем уже существует в этой группе'}}},
        },
        operation_id='characteristic_templates_create',
    ),
)
class CharacteristicTemplateListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком шаблонов характеристик.

    **GET** — получение списка шаблонов (доступно всем).
    **POST** — создание нового шаблона (только для администраторов).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request):
        """Получить список всех шаблонов характеристик."""
        from .models import CharacteristicTemplate
        templates = CharacteristicTemplate.objects.all().select_related('group').order_by('group', 'order')

        serializer = CharacteristicTemplateListSerializer(templates, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Создать новый шаблон характеристики."""
        serializer = CharacteristicTemplateCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                group_id = serializer.validated_data['group']
                template = CharacteristicTemplateService.create_template(
                    user=request.user,
                    group_id=group_id,
                    name=serializer.validated_data['name'],
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en'),
                    order=serializer.validated_data.get('order', 0)
                )
                logger.info(f"Шаблон характеристики создан: '{template.name}' (пользователь: {request.user.email})")
                from django.urls import reverse
                headers = {'Location': reverse('characteristic-template-detail', args=[template.pk])}
                return Response(
                    CharacteristicTemplateDetailSerializer(template).data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            except PermissionError as e:
                logger.warning(f"Попытка создания шаблона без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Шаблоны характеристик'],
        summary='Получение детальной информации о шаблоне характеристики',
        description=(
            'Получить полную информацию о шаблоне характеристики по его идентификатору.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/characteristic/templates/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор шаблона',
                examples=[OpenApiExample('ID шаблона', value=1)],
            ),
        ],
        responses={
            200: CharacteristicTemplateDetailSerializer,
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Шаблон характеристики не найден'}}},
        },
        operation_id='characteristic_templates_retrieve',
    ),
    put=extend_schema(
        tags=['Шаблоны характеристик'],
        summary='Обновление шаблона характеристики',
        description=(
            'Обновить данные шаблона характеристики.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PUT /api/characteristic/characteristic/templates/1/\n'
            '{\n'
            '  "name": "Обновлённый шаблон",\n'
            '  "name_ru": "Обновлённый шаблон",\n'
            '  "name_en": "Updated Template",\n'
            '  "order": 10\n'
            '}\n'
            '```'
        ),
        request=CharacteristicTemplateUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор шаблона',
                examples=[OpenApiExample('ID шаблона', value=1)],
            ),
        ],
        responses={
            200: CharacteristicTemplateDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять шаблоны характеристик'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Шаблон характеристики не найден'}}},
        },
        operation_id='characteristic_templates_update',
    ),
    delete=extend_schema(
        tags=['Шаблоны характеристик'],
        summary='Удаление шаблона характеристики',
        description=(
            'Безвозвратно удалить шаблон характеристики.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример:**\n'
            '```\n'
            'DELETE /api/characteristic/characteristic/templates/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор шаблона',
                examples=[OpenApiExample('ID шаблона', value=1)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Шаблон характеристики успешно удален'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут удалять шаблоны характеристик'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Шаблон характеристики не найден'}}},
        },
        operation_id='characteristic_templates_destroy',
    ),
)
class CharacteristicTemplateDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельным шаблоном характеристики.

    **GET** — получение детальной информации (доступно всем).
    **PUT** — обновление шаблона (только администраторы).
    **DELETE** — удаление шаблона (только администраторы).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk: int):
        """Получить детальную информацию о шаблоне характеристики."""
        try:
            template = CharacteristicTemplateService.get_template_detail(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CharacteristicTemplateDetailSerializer(template)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk: int):
        """Обновить шаблон характеристики."""
        serializer = CharacteristicTemplateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                template = CharacteristicTemplateService.get_template_detail(pk)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

            try:
                template = CharacteristicTemplateService.update_template(
                    user=request.user,
                    template_id=pk,
                    name=serializer.validated_data.get('name'),
                    name_ru=serializer.validated_data.get('name_ru'),
                    name_en=serializer.validated_data.get('name_en'),
                    order=serializer.validated_data.get('order')
                )
                logger.info(f"Шаблон характеристики обновлён: ID={pk} (пользователь: {request.user.email})")
                return Response(
                    CharacteristicTemplateDetailSerializer(template).data,
                    status=status.HTTP_200_OK
                )
            except PermissionError as e:
                logger.warning(f"Попытка изменения шаблона без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk: int):
        """Удалить шаблон характеристики."""
        try:
            CharacteristicTemplateService.delete_template(
                user=request.user,
                template_id=pk
            )
            logger.info(f"Шаблон характеристики удалён: ID={pk} (пользователь: {request.user.email})")
            return Response(
                {'message': 'Шаблон характеристики успешно удален'},
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка удаления шаблона без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)


# =============================================================================
# ProductCharacteristic Views (CharacteristicValue)
# =============================================================================

@extend_schema_view(
    get=extend_schema(
        tags=['Характеристики товара'],
        summary='Получение списка характеристик товара',
        description=(
            'Получить все значения характеристик для указанного товара.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/products/1/characteristics/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=1)],
            ),
        ],
        responses={
            200: CharacteristicValueListSerializer(many=True),
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Товар не найден'}}},
        },
        operation_id='product_characteristics_list',
    ),
    post=extend_schema(
        tags=['Характеристики товара'],
        summary='Создание характеристики товара',
        description=(
            'Создать новое значение характеристики для товара.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n'
            '- Товар и шаблон должны существовать\n'
            '- Характеристика с таким шаблоном не должна существовать для этого товара\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'POST /api/characteristic/products/1/characteristics/\n'
            '{\n'
            '  "value": "200г",\n'
            '  "value_ru": "200г",\n'
            '  "value_en": "200g",\n'
            '  "product": 1,\n'
            '  "template": 1\n'
            '}\n'
            '```'
        ),
        request=CharacteristicValueCreateSerializer,
        responses={
            201: CharacteristicValueDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут добавлять характеристики товаров'}}},
            409: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Характеристика уже существует для этого товара'}}},
        },
        operation_id='product_characteristics_create',
    ),
)
class ProductCharacteristicListCreateView(APIView):
    """
    REST API эндпоинт для работы со списком характеристик товара.

    **GET** — получение списка характеристик (доступно всем).
    **POST** — создание новой характеристики (только для администраторов).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int):
        """Получить все характеристики товара."""
        from products.services import ProductService
        try:
            ProductService.get_product_detail(id)
        except ValueError:
            return Response({'error': 'Товар не найден'}, status=status.HTTP_404_NOT_FOUND)

        try:
            values = CharacteristicValueService.get_values_by_product(id)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CharacteristicValueListSerializer(values, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, id: int):
        """Создать характеристику товара."""
        serializer = CharacteristicValueCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                product_id = serializer.validated_data['product']
                template_id = serializer.validated_data['template']
                value = CharacteristicValueService.create_value(
                    user=request.user,
                    product_id=product_id,
                    template_id=template_id,
                    value=serializer.validated_data['value'],
                    value_ru=serializer.validated_data.get('value_ru'),
                    value_en=serializer.validated_data.get('value_en')
                )
                logger.info(f"Характеристика товара создана (пользователь: {request.user.email})")
                from django.urls import reverse
                headers = {'Location': reverse('product-characteristic-detail', args=[id, value.pk])}
                return Response(
                    CharacteristicValueDetailSerializer(value).data,
                    status=status.HTTP_201_CREATED,
                    headers=headers
                )
            except PermissionError as e:
                logger.warning(f"Попытка создания характеристики без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        tags=['Характеристики товара'],
        summary='Получение детальной информации о характеристике товара',
        description=(
            'Получить полную информацию о значении характеристики по её идентификатору.\n\n'
            '**Доступ:** всем пользователям (включая неавторизованных).\n\n'
            '**Пример:**\n'
            '```\n'
            'GET /api/characteristic/products/1/characteristics/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=1)],
            ),
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор значения характеристики',
                examples=[OpenApiExample('ID характеристики', value=1)],
            ),
        ],
        responses={
            200: CharacteristicValueDetailSerializer,
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Значение характеристики не найдено'}}},
        },
        operation_id='product_characteristics_retrieve',
    ),
    put=extend_schema(
        tags=['Характеристики товара'],
        summary='Обновление характеристики товара',
        description=(
            'Обновить значение характеристики.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример запроса:**\n'
            '```\n'
            'PUT /api/characteristic/products/1/characteristics/1/\n'
            '{\n'
            '  "value": "300г",\n'
            '  "value_ru": "300г",\n'
            '  "value_en": "300g"\n'
            '}\n'
            '```'
        ),
        request=CharacteristicValueUpdateSerializer,
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=1)],
            ),
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор значения характеристики',
                examples=[OpenApiExample('ID характеристики', value=1)],
            ),
        ],
        responses={
            200: CharacteristicValueDetailSerializer,
            400: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Ошибка валидации'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут изменять характеристики товаров'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Значение характеристики не найдено'}}},
        },
        operation_id='product_characteristics_update',
    ),
    delete=extend_schema(
        tags=['Характеристики товара'],
        summary='Удаление характеристики товара',
        description=(
            'Безвозвратно удалить значение характеристики.\n\n'
            '**Требования:**\n'
            '- Только для администраторов\n\n'
            '**Пример:**\n'
            '```\n'
            'DELETE /api/characteristic/products/1/characteristics/1/\n'
            '```'
        ),
        parameters=[
            OpenApiParameter(
                name='id',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор товара',
                examples=[OpenApiExample('ID товара', value=1)],
            ),
            OpenApiParameter(
                name='pk',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.PATH,
                description='Уникальный идентификатор значения характеристики',
                examples=[OpenApiExample('ID характеристики', value=1)],
            ),
        ],
        responses={
            200: {'type': 'object', 'properties': {'message': {'type': 'string', 'example': 'Характеристика товара успешно удалена'}}},
            401: {'type': 'object', 'properties': {'detail': {'type': 'string', 'example': 'Учетные данные не предоставлены.'}}},
            403: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Только администраторы могут удалять характеристики товаров'}}},
            404: {'type': 'object', 'properties': {'error': {'type': 'string', 'example': 'Значение характеристики не найдено'}}},
        },
        operation_id='product_characteristics_destroy',
    ),
)
class ProductCharacteristicDetailView(APIView):
    """
    REST API эндпоинт для работы с отдельным значением характеристики товара.

    **GET** — получение детальной информации (доступно всем).
    **PUT** — обновление характеристики (только администраторы).
    **DELETE** — удаление характеристики (только администраторы).
    """
    def get_permissions(self):
        """Возвращает список классов разрешений для запроса."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, id: int, pk: int):
        """Получить детальную информацию о характеристике товара."""
        try:
            value = CharacteristicValueService.get_value_detail(pk)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

        serializer = CharacteristicValueDetailSerializer(value)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id: int, pk: int):
        """Обновить характеристику товара."""
        serializer = CharacteristicValueUpdateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                value = CharacteristicValueService.get_value_detail(pk)
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)

            try:
                value = CharacteristicValueService.update_value(
                    user=request.user,
                    value_id=pk,
                    value=serializer.validated_data.get('value'),
                    value_ru=serializer.validated_data.get('value_ru'),
                    value_en=serializer.validated_data.get('value_en')
                )
                logger.info(f"Характеристика товара обновлена: ID={pk} (пользователь: {request.user.email})")
                return Response(
                    CharacteristicValueDetailSerializer(value).data,
                    status=status.HTTP_200_OK
                )
            except PermissionError as e:
                logger.warning(f"Попытка изменения характеристики без прав: {request.user.email}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_403_FORBIDDEN
                )
            except ValueError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_409_CONFLICT
                )
        return Response(
            {'error': 'Ошибка валидации', 'details': serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, id: int, pk: int):
        """Удалить характеристику товара."""
        try:
            CharacteristicValueService.delete_value(
                user=request.user,
                value_id=pk
            )
            logger.info(f"Характеристика товара удалена: ID={pk} (пользователь: {request.user.email})")
            return Response(
                {'message': 'Характеристика товара успешно удалена'},
                status=status.HTTP_200_OK
            )
        except PermissionError as e:
            logger.warning(f"Попытка удаления характеристики без прав: {request.user.email}")
            return Response({'error': str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
