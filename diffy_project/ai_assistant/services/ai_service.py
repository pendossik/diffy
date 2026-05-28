import json
from catalog.models import Product
from .openrouter import call_openrouter_llm
from ..prompts.templates import SYSTEM_PROMPT, get_user_prompt
from django.utils.translation import get_language

def generate_comparison_summary(product_ids: list[int]) -> str:
    # --- МЕСТО ДЛЯ КЭШИРОВАНИЯ ---
    # В будущем здесь можно добавить логику:
    # cache_key = f"ai_compare_{'_'.join(map(str, sorted(product_ids)))}"
    # cached_result = cache.get(cache_key)
    # if cached_result: return cached_result
    # -----------------------------

    # 1. Получаем данные (используем ту же оптимизацию, что и у тебя)
    products = (
        Product.objects.filter(id__in=product_ids)
        .select_related("category")
        .prefetch_related("characteristic_values__template__group")
    )

    if len(products) < 2:
        return "Для сравнения нужно минимум 2 товара."

    # 2. Формируем данные в словарь для ИИ
    products_data = []
    for product in products:
        chars_list = []
        for val in product.characteristic_values.all():
            chars_list.append(f"{val.template.name}: {val.value}")
            
        products_data.append({
            "name": product.name,
            "category": product.category.name,
            "characteristics": chars_list
        })

    # 3. Превращаем в JSON строку
    products_json_str = json.dumps(products_data, ensure_ascii=False, indent=2)

    # 4. Формируем промпт и делаем запрос
    current_lang = get_language()  # Вернет 'ru' или 'en'
    user_prompt = get_user_prompt(products_json_str, lang=current_lang)
    
    try:
        ai_response = call_openrouter_llm(SYSTEM_PROMPT, user_prompt)
        
        # --- МЕСТО ДЛЯ СОХРАНЕНИЯ В КЭШ ---
        # cache.set(cache_key, ai_response, timeout=60*60*24*7) # кэш на неделю
        # ----------------------------------
        
        return ai_response
    except Exception as e:
        return "Извините, в данный момент ИИ-ассистент недоступен. Попробуйте позже."