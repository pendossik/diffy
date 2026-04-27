class ValidationError(Exception):
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class FieldRequiredError(ValidationError):
    def __init__(self, field: str):
        self.field = field
        self.message = f"Поле '{field}' обязательно"
        super().__init__(field, self.message)


class FieldMaxLengthError(ValidationError):
    def __init__(self, field: str, max_length: int):
        self.field = field
        self.max_length = max_length
        self.message = f"Поле '{field}' не должно превышать {max_length} символов"
        super().__init__(field, self.message)


class FieldMinLengthError(ValidationError):
    def __init__(self, field: str, min_length: int):
        self.field = field
        self.min_length = min_length
        self.message = f"Поле '{field}' должно быть не менее {min_length} символов"
        super().__init__(field, self.message)


class FieldEmptyError(ValidationError):
    def __init__(self, field: str):
        self.field = field
        self.message = f"Поле '{field}' не может быть пустым"
        super().__init__(field, self.message)


class InvalidFormatError(ValidationError):
    def __init__(self, field: str, expected_format: str):
        self.field = field
        self.expected_format = expected_format
        self.message = f"Поле '{field}' имеет неверный формат. Ожидается: {expected_format}"
        super().__init__(field, self.message)


class ObjectNotFoundError(ValidationError):
    def __init__(self, model_name: str, object_id: int):
        self.model_name = model_name
        self.object_id = object_id
        self.message = f"{model_name} с ID={object_id} не найден"
        super().__init__('id', self.message)


class ObjectAlreadyExistsError(ValidationError):
    def __init__(self, model_name: str, field_name: str, field_value: str):
        self.model_name = model_name
        self.field_name = field_name
        self.field_value = field_value
        self.message = f"{model_name} с {field_name}='{field_value}' уже существует"
        super().__init__(field_name, self.message)


class PermissionDeniedError(ValidationError):
    def __init__(self, message: str = "Доступ запрещен"):
        self.message = message
        super().__init__('permission', message)