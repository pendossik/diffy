class RepositoryError(Exception):
    pass


class ObjectNotFoundError(RepositoryError):
    def __init__(self, model_name: str, object_id: int):
        self.model_name = model_name
        self.object_id = object_id
        super().__init__(f"{model_name} с ID={object_id} не найден")


class ObjectAlreadyExistsError(RepositoryError):
    def __init__(self, model_name: str, field_name: str, field_value: str):
        self.model_name = model_name
        self.field_name = field_name
        self.field_value = field_value
        super().__init__(f"{model_name} с {field_name}='{field_value}' уже существует")


class InvalidDataError(RepositoryError):
    def __init__(self, field_name: str, message: str):
        self.field_name = field_name
        self.message = message
        super().__init__(f"Некорректное значение для '{field_name}': {message}")


class RelatedObjectNotFoundError(RepositoryError):
    def __init__(self, related_model: str, related_id: int):
        self.related_model = related_model
        self.related_id = related_id
        super().__init__(f"{related_model} с ID={related_id} не найден")