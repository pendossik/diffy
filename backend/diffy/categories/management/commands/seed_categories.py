"""Management command для генерации тестовых категорий."""
import random
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from categories.models import Category

logger = logging.getLogger('categories')


# 📦 Датасет: 1000 категорий, сгруппированных по доменам
# Формат: (name_ru, name_en)
CATEGORIES_DATASET = [
    # 💻 Технологии и IT (150)
    ("Python", "Python"), ("JavaScript", "JavaScript"), ("TypeScript", "TypeScript"),
    ("React", "React"), ("Vue.js", "Vue.js"), ("Angular", "Angular"),
    ("Django", "Django"), ("Flask", "Flask"), ("FastAPI", "FastAPI"),
    ("PostgreSQL", "PostgreSQL"), ("MongoDB", "MongoDB"), ("Redis", "Redis"),
    ("Docker", "Docker"), ("Kubernetes", "Kubernetes"), ("Git", "Git"),
    ("Linux", "Linux"), ("Windows", "Windows"), ("macOS", "macOS"),
    ("Android", "Android"), ("iOS", "iOS"), ("Flutter", "Flutter"),
    ("Swift", "Swift"), ("Kotlin", "Kotlin"), ("Java", "Java"),
    ("C++", "C++"), ("C#", "C#"), ("Go", "Go"), ("Rust", "Rust"),
    ("PHP", "PHP"), ("Ruby", "Ruby"), ("Perl", "Perl"),
    ("HTML", "HTML"), ("CSS", "CSS"), ("SASS", "SASS"),
    ("Webpack", "Webpack"), ("Vite", "Vite"), ("Babel", "Babel"),
    ("TensorFlow", "TensorFlow"), ("PyTorch", "PyTorch"), ("Scikit-learn", "Scikit-learn"),
    ("Pandas", "Pandas"), ("NumPy", "NumPy"), ("Matplotlib", "Matplotlib"),
    ("AWS", "AWS"), ("Google Cloud", "Google Cloud"), ("Azure", "Azure"),
    ("CI/CD", "CI/CD"), ("Jenkins", "Jenkins"), ("GitHub Actions", "GitHub Actions"),
    ("GraphQL", "GraphQL"), ("REST API", "REST API"), ("WebSocket", "WebSocket"),
    ("OAuth", "OAuth"), ("JWT", "JWT"), ("SSL/TLS", "SSL/TLS"),
    ("VPN", "VPN"), ("Firewall", "Firewall"), ("Encryption", "Encryption"),
    ("Machine Learning", "Machine Learning"), ("Deep Learning", "Deep Learning"),
    ("NLP", "NLP"), ("Computer Vision", "Computer Vision"), ("Robotics", "Robotics"),
    ("IoT", "IoT"), ("Blockchain", "Blockchain"), ("Cryptocurrency", "Cryptocurrency"),
    ("Smart Contract", "Smart Contract"), ("Web3", "Web3"), ("Metaverse", "Metaverse"),
    ("VR", "VR"), ("AR", "AR"), ("3D Printing", "3D Printing"),
    ("Cybersecurity", "Cybersecurity"), ("Penetration Testing", "Penetration Testing"),
    ("Data Science", "Data Science"), ("Big Data", "Big Data"), ("ETL", "ETL"),
    ("Apache Spark", "Apache Spark"), ("Kafka", "Kafka"), ("Elasticsearch", "Elasticsearch"),
    ("Microservices", "Microservices"), ("Serverless", "Serverless"), ("Edge Computing", "Edge Computing"),
    ("Quantum Computing", "Quantum Computing"), ("Neural Network", "Neural Network"),
    ("Algorithm", "Algorithm"), ("Data Structure", "Data Structure"), ("Design Pattern", "Design Pattern"),
    ("Agile", "Agile"), ("Scrum", "Scrum"), ("Kanban", "Kanban"),
    ("DevOps", "DevOps"), ("SRE", "SRE"), ("QA", "QA"),
    ("Unit Testing", "Unit Testing"), ("Integration Testing", "Integration Testing"),
    ("Load Testing", "Load Testing"), ("Security Audit", "Security Audit"),
    ("Code Review", "Code Review"), ("Refactoring", "Refactoring"),
    ("Technical Debt", "Technical Debt"), ("Documentation", "Documentation"),
    ("API Gateway", "API Gateway"), ("Load Balancer", "Load Balancer"),
    ("CDN", "CDN"), ("DNS", "DNS"), ("SMTP", "SMTP"),
    ("WebSocket", "WebSocket"), ("gRPC", "gRPC"), ("Protobuf", "Protobuf"),
    ("JSON", "JSON"), ("XML", "XML"), ("YAML", "YAML"),
    ("Markdown", "Markdown"), ("LaTeX", "LaTeX"), ("SVG", "SVG"),
    ("WebGL", "WebGL"), ("Three.js", "Three.js"), ("D3.js", "D3.js"),
    ("Tailwind CSS", "Tailwind CSS"), ("Bootstrap", "Bootstrap"), ("Material UI", "Material UI"),
    ("Next.js", "Next.js"), ("Nuxt.js", "Nuxt.js"), ("Svelte", "Svelte"),
    ("Electron", "Electron"), ("Tauri", "Tauri"), ("React Native", "React Native"),
    ("Xamarin", "Xamarin"), ("Unity", "Unity"), ("Unreal Engine", "Unreal Engine"),
    ("Blender", "Blender"), ("Figma", "Figma"), ("Adobe XD", "Adobe XD"),
    ("Photoshop", "Photoshop"), ("Illustrator", "Illustrator"), ("Premiere Pro", "Premiere Pro"),
    ("After Effects", "After Effects"), ("Audacity", "Audacity"), ("OBS Studio", "OBS Studio"),
    ("VS Code", "VS Code"), ("PyCharm", "PyCharm"), ("IntelliJ IDEA", "IntelliJ IDEA"),
    ("WebStorm", "WebStorm"), ("Android Studio", "Android Studio"), ("Xcode", "Xcode"),
    ("Vim", "Vim"), ("Emacs", "Emacs"), ("Neovim", "Neovim"),
    ("Terminal", "Terminal"), ("Bash", "Bash"), ("PowerShell", "PowerShell"),
    ("Regex", "Regex"), ("SQL", "SQL"), ("NoSQL", "NoSQL"),
    ("ORM", "ORM"), ("Migration", "Migration"), ("Seed Data", "Seed Data"),
    ("Authentication", "Authentication"), ("Authorization", "Authorization"),
    ("RBAC", "RBAC"), ("ABAC", "ABAC"), ("SSO", "SSO"),
    ("MFA", "MFA"), ("Biometrics", "Biometrics"), ("Password Manager", "Password Manager"),
    
    # 🌿 Природа и экология (150)
    ("Лес", "Forest"), ("Тайга", "Taiga"), ("Тундра", "Tundra"),
    ("Степь", "Steppe"), ("Пустыня", "Desert"), ("Джунгли", "Jungle"),
    ("Горы", "Mountains"), ("Холмы", "Hills"), ("Долина", "Valley"),
    ("Каньон", "Canyon"), ("Ущелье", "Gorge"), ("Плато", "Plateau"),
    ("Вулкан", "Volcano"), ("Ледник", "Glacier"), ("Айсберг", "Iceberg"),
    ("Океан", "Ocean"), ("Море", "Sea"), ("Залив", "Bay"),
    ("Пролив", "Strait"), ("Остров", "Island"), ("Полуостров", "Peninsula"),
    ("Река", "River"), ("Озеро", "Lake"), ("Пруд", "Pond"),
    ("Водопад", "Waterfall"), ("Родник", "Spring"), ("Болото", "Swamp"),
    ("Пещера", "Cave"), ("Грот", "Grotto"), ("Скалы", "Cliffs"),
    ("Песок", "Sand"), ("Галька", "Pebbles"), ("Глина", "Clay"),
    ("Гранит", "Granite"), ("Мрамор", "Marble"), ("Базальт", "Basalt"),
    ("Алмаз", "Diamond"), ("Золото", "Gold"), ("Серебро", "Silver"),
    ("Медь", "Copper"), ("Железо", "Iron"), ("Алюминий", "Aluminum"),
    ("Нефть", "Oil"), ("Газ", "Gas"), ("Уголь", "Coal"),
    ("Торф", "Peat"), ("Уран", "Uranium"), ("Литий", "Lithium"),
    ("Солнце", "Sun"), ("Луна", "Moon"), ("Звёзды", "Stars"),
    ("Планета", "Planet"), ("Галактика", "Galaxy"), ("Туманность", "Nebula"),
    ("Комета", "Comet"), ("Метеор", "Meteor"), ("Астероид", "Asteroid"),
    ("Дождь", "Rain"), ("Снег", "Snow"), ("Град", "Hail"),
    ("Туман", "Fog"), ("Роса", "Dew"), ("Иней", "Frost"),
    ("Ветер", "Wind"), ("Ураган", "Hurricane"), ("Торнадо", "Tornado"),
    ("Гроза", "Thunderstorm"), ("Молния", "Lightning"), ("Радуга", "Rainbow"),
    ("Облака", "Clouds"), ("Небо", "Sky"), ("Горизонт", "Horizon"),
    ("Рассвет", "Dawn"), ("Закат", "Sunset"), ("Полночь", "Midnight"),
    ("Весна", "Spring"), ("Лето", "Summer"), ("Осень", "Autumn"),
    ("Зима", "Winter"), ("Экватор", "Equator"), ("Полюс", "Pole"),
    ("Дуб", "Oak"), ("Берёза", "Birch"), ("Сосна", "Pine"),
    ("Ель", "Spruce"), ("Клён", "Maple"), ("Липа", "Linden"),
    ("Роза", "Rose"), ("Тюльпан", "Tulip"), ("Орхидея", "Orchid"),
    ("Кактус", "Cactus"), ("Папоротник", "Fern"), ("Мох", "Moss"),
    ("Гриб", "Mushroom"), ("Водоросли", "Algae"), ("Лишайник", "Lichen"),
    ("Лев", "Lion"), ("Тигр", "Tiger"), ("Леопард", "Leopard"),
    ("Слон", "Elephant"), ("Носорог", "Rhino"), ("Жираф", "Giraffe"),
    ("Зебра", "Zebra"), ("Обезьяна", "Monkey"), ("Горилла", "Gorilla"),
    ("Медведь", "Bear"), ("Волк", "Wolf"), ("Лиса", "Fox"),
    ("Заяц", "Hare"), ("Белка", "Squirrel"), ("Ёж", "Hedgehog"),
    ("Олень", "Deer"), ("Лось", "Moose"), ("Кабан", "Boar"),
    ("Орёл", "Eagle"), ("Сокол", "Falcon"), ("Сова", "Owl"),
    ("Ворон", "Raven"), ("Воробей", "Sparrow"), ("Ласточка", "Swallow"),
    ("Пингвин", "Penguin"), ("Фламинго", "Flamingo"), ("Попугай", "Parrot"),
    ("Акула", "Shark"), ("Дельфин", "Dolphin"), ("Кит", "Whale"),
    ("Осьминог", "Octopus"), ("Медуза", "Jellyfish"), ("Краб", "Crab"),
    ("Лосось", "Salmon"), ("Тунец", "Tuna"), ("Карп", "Carp"),
    ("Змея", "Snake"), ("Ящерица", "Lizard"), ("Черепаха", "Turtle"),
    ("Лягушка", "Frog"), ("Саламандра", "Salamander"), ("Тритон", "Newt"),
    ("Пчела", "Bee"), ("Бабочка", "Butterfly"), ("Стрекоза", "Dragonfly"),
    ("Муравей", "Ant"), ("Паук", "Spider"), ("Скорпион", "Scorpion"),
    ("Комар", "Mosquito"), ("Муха", "Fly"), ("Жук", "Beetle"),
    ("Коралл", "Coral"), ("Губка", "Sponge"), ("Морская звезда", "Starfish"),
    ("Экосистема", "Ecosystem"), ("Биосфера", "Biosphere"), ("Климат", "Climate"),
    ("Погода", "Weather"), ("Сейсмика", "Seismic"), ("Эрозия", "Erosion"),
    
    # 🍽 Еда и кулинария (100)
    ("Борщ", "Borscht"), ("Щи", "Shchi"), ("Солянка", "Solyanka"),
    ("Пельмени", "Dumplings"), ("Вареники", "Vareniki"), ("Голубцы", "Cabbage Rolls"),
    ("Бефстроганов", "Beef Stroganoff"), ("Шашлык", "Shashlik"), ("Плов", "Pilaf"),
    ("Хинкали", "Khinkali"), ("Хачапури", "Khachapuri"), ("Блинчики", "Blini"),
    ("Сырники", "Syrniki"), ("Оладьи", "Pancakes"), ("Каша", "Porridge"),
    ("Суп", "Soup"), ("Бульон", "Broth"), ("Рассольник", "Rassolnik"),
    ("Окрошка", "Okroshka"), ("Уха", "Fish Soup"), ("Соус", "Sauce"),
    ("Салат", "Salad"), ("Винегрет", "Vinaigrette"), ("Оливье", "Olivier"),
    ("Пицца", "Pizza"), ("Паста", "Pasta"), ("Ризотто", "Risotto"),
    ("Лазанья", "Lasagna"), ("Рагу", "Ragout"), ("Гуляш", "Goulash"),
    ("Стейк", "Steak"), ("Котлета", "Cutlet"), ("Тефтели", "Meatballs"),
    ("Курица", "Chicken"), ("Индейка", "Turkey"), ("Утка", "Duck"),
    ("Говядина", "Beef"), ("Свинина", "Pork"), ("Баранина", "Lamb"),
    ("Рыба", "Fish"), ("Лосось", "Salmon"), ("Треска", "Cod"),
    ("Креветки", "Shrimp"), ("Мидии", "Mussels"), ("Кальмары", "Squid"),
    ("Яйца", "Eggs"), ("Сыр", "Cheese"), ("Молоко", "Milk"),
    ("Сливки", "Cream"), ("Сметана", "Sour Cream"), ("Творог", "Cottage Cheese"),
    ("Масло", "Butter"), ("Маргарин", "Margarine"), ("Йогурт", "Yogurt"),
    ("Хлеб", "Bread"), ("Батон", "Loaf"), ("Багет", "Baguette"),
    ("Булка", "Bun"), ("Круассан", "Croissant"), ("Бублик", "Bagel"),
    ("Печенье", "Cookies"), ("Торт", "Cake"), ("Пирог", "Pie"),
    ("Кекс", "Muffin"), ("Вафли", "Waffles"), ("Мороженое", "Ice Cream"),
    ("Шоколад", "Chocolate"), ("Конфеты", "Candies"), ("Мармелад", "Marmalade"),
    ("Пастила", "Pastila"), ("Халва", "Halva"), ("Козинаки", "Gozinaki"),
    ("Мёд", "Honey"), ("Варенье", "Jam"), ("Джем", "Jelly"),
    ("Сахар", "Sugar"), ("Соль", "Salt"), ("Перец", "Pepper"),
    ("Специи", "Spices"), ("Травы", "Herbs"), ("Чеснок", "Garlic"),
    ("Лук", "Onion"), ("Морковь", "Carrot"), ("Картофель", "Potato"),
    ("Капуста", "Cabbage"), ("Огурец", "Cucumber"), ("Помидор", "Tomato"),
    ("Яблоко", "Apple"), ("Груша", "Pear"), ("Слива", "Plum"),
    ("Вишня", "Cherry"), ("Клубника", "Strawberry"), ("Малина", "Raspberry"),
    ("Смородина", "Currant"), ("Крыжовник", "Gooseberry"), ("Арбуз", "Watermelon"),
    ("Дыня", "Melon"), ("Виноград", "Grapes"), ("Апельсин", "Orange"),
    ("Лимон", "Lemon"), ("Лайм", "Lime"), ("Грейпфрут", "Grapefruit"),
    ("Банан", "Banana"), ("Киви", "Kiwi"), ("Ананас", "Pineapple"),
    ("Манго", "Mango"), ("Авокадо", "Avocado"), ("Кокос", "Coconut"),
    ("Орехи", "Nuts"), ("Миндаль", "Almond"), ("Фундук", "Hazelnut"),
    ("Кешью", "Cashew"), ("Фисташки", "Pistachios"), ("Арахис", "Peanuts"),
    ("Кофе", "Coffee"), ("Чай", "Tea"), ("Какао", "Cocoa"),
    ("Сок", "Juice"), ("Компот", "Compote"), ("Квас", "Kvass"),
    ("Вода", "Water"), ("Лимонад", "Lemonade"), ("Смузи", "Smoothie"),
    ("Вино", "Wine"), ("Пиво", "Beer"), ("Водка", "Vodka"),
    ("Коньяк", "Cognac"), ("Виски", "Whiskey"), ("Джин", "Gin"),
    
    # 🏗️ Архитектура и сооружения (100)
    ("Дом", "House"), ("Квартира", "Apartment"), ("Коттедж", "Cottage"),
    ("Вилла", "Villa"), ("Замок", "Castle"), ("Дворец", "Palace"),
    ("Небоскрёб", "Skyscraper"), ("Башня", "Tower"), ("Мост", "Bridge"),
    ("Тоннель", "Tunnel"), ("Дамба", "Dam"), ("Плотина", "Weir"),
    ("Аэропорт", "Airport"), ("Вокзал", "Train Station"), ("Метро", "Subway"),
    ("Стадион", "Stadium"), ("Театр", "Theater"), ("Кинотеатр", "Cinema"),
    ("Музей", "Museum"), ("Библиотека", "Library"), ("Школа", "School"),
    ("Университет", "University"), ("Больница", "Hospital"), ("Церковь", "Church"),
    ("Мечеть", "Mosque"), ("Синагога", "Synagogue"), ("Храм", "Temple"),
    ("Памятник", "Monument"), ("Фонтан", "Fountain"), ("Парк", "Park"),
    ("Сад", "Garden"), ("Аллея", "Alley"), ("Площадь", "Square"),
    ("Улица", "Street"), ("Проспект", "Avenue"), ("Бульвар", "Boulevard"),
    ("Набережная", "Embankment"), ("Переулок", "Lane"), ("Тупик", "Cul-de-sac"),
    ("Гараж", "Garage"), ("Склад", "Warehouse"), ("Завод", "Factory"),
    ("Офис", "Office"), ("Бизнес-центр", "Business Center"), ("ТЦ", "Shopping Mall"),
    ("Рынок", "Market"), ("Магазин", "Store"), ("Ресторан", "Restaurant"),
    ("Кафе", "Cafe"), ("Бар", "Bar"), ("Отель", "Hotel"),
    ("Хостел", "Hostel"), ("Мотель", "Motel"), ("Кемпинг", "Campsite"),
    ("Дача", "Dacha"), ("Баня", "Banya"), ("Сауна", "Sauna"),
    ("Бассейн", "Pool"), ("Спортзал", "Gym"), ("Каток", "Ice Rink"),
    ("Стадион", "Stadium"), ("Корт", "Court"), ("Поле", "Field"),
    ("Трек", "Track"), ("Велодорожка", "Bike Path"), ("Парковка", "Parking"),
    ("Забор", "Fence"), ("Ворота", "Gate"), ("Калитка", "Wicket"),
    ("Крыльцо", "Porch"), ("Балкон", "Balcony"), ("Лоджия", "Loggia"),
    ("Терраса", "Terrace"), ("Веранда", "Veranda"), ("Мансарда", "Attic"),
    ("Подвал", "Basement"), ("Чердак", "Loft"), ("Лестница", "Stairs"),
    ("Лифт", "Elevator"), ("Эскалатор", "Escalator"), ("Пандус", "Ramp"),
    ("Крыша", "Roof"), ("Стена", "Wall"), ("Потолок", "Ceiling"),
    ("Пол", "Floor"), ("Окно", "Window"), ("Дверь", "Door"),
    ("Готика", "Gothic"), ("Барокко", "Baroque"), ("Рококо", "Rococo"),
    ("Классицизм", "Classicism"), ("Модерн", "Art Nouveau"), ("Арт-деко", "Art Deco"),
    ("Конструктивизм", "Constructivism"), ("Брутализм", "Brutalism"), ("Хай-тек", "High-tech"),
    ("Минимализм", "Minimalism"), ("Эко-стиль", "Eco-style"), ("Лофт", "Loft"),
    ("Сканди", "Scandi"), ("Японский стиль", "Japanese Style"), ("Кантри", "Country"),
    ("Кирпич", "Brick"), ("Бетон", "Concrete"), ("Дерево", "Wood"),
    ("Стекло", "Glass"), ("Металл", "Metal"), ("Пластик", "Plastic"),
    ("Камень", "Stone"), ("Мрамор", "Marble"), ("Керамика", "Ceramics"),
    
    # 🎨 Искусство и культура (100)
    ("Живопись", "Painting"), ("Графика", "Graphics"), ("Скульптура", "Sculpture"),
    ("Архитектура", "Architecture"), ("Фотография", "Photography"), ("Дизайн", "Design"),
    ("Иллюстрация", "Illustration"), ("Каллиграфия", "Calligraphy"), ("Гравюра", "Engraving"),
    ("Импрессионизм", "Impressionism"), ("Экспрессионизм", "Expressionism"), ("Кубизм", "Cubism"),
    ("Сюрреализм", "Surrealism"), ("Абстракционизм", "Abstract"), ("Поп-арт", "Pop Art"),
    ("Стрит-арт", "Street Art"), ("Граффити", "Graffiti"), ("Инсталляция", "Installation"),
    ("Перформанс", "Performance"), ("Видео-арт", "Video Art"), ("Цифровое искусство", "Digital Art"),
    ("Музыка", "Music"), ("Классика", "Classical"), ("Джаз", "Jazz"),
    ("Рок", "Rock"), ("Поп", "Pop"), ("Хип-хоп", "Hip-hop"),
    ("Электронная", "Electronic"), ("Фолк", "Folk"), ("Блюз", "Blues"),
    ("Кантри", "Country"), ("Регги", "Reggae"), ("Метал", "Metal"),
    ("Панк", "Punk"), ("Инди", "Indie"), ("Лоу-фай", "Lo-fi"),
    ("Опера", "Opera"), ("Балет", "Ballet"), ("Мюзикл", "Musical"),
    ("Драма", "Drama"), ("Комедия", "Comedy"), ("Трагедия", "Tragedy"),
    ("Фарс", "Farce"), ("Импровизация", "Improv"), ("Стендап", "Stand-up"),
    ("Кино", "Cinema"), ("Фильм", "Film"), ("Сериал", "TV Series"),
    ("Документальный", "Documentary"), ("Анимация", "Animation"), ("Мультфильм", "Cartoon"),
    ("Боевик", "Action"), ("Триллер", "Thriller"), ("Ужасы", "Horror"),
    ("Фантастика", "Sci-Fi"), ("Фэнтези", "Fantasy"), ("Мелодрама", "Romance"),
    ("Детектив", "Detective"), ("Вестерн", "Western"), ("Исторический", "Historical"),
    ("Литература", "Literature"), ("Поэзия", "Poetry"), ("Проза", "Prose"),
    ("Роман", "Novel"), ("Рассказ", "Short Story"), ("Эссе", "Essay"),
    ("Мемуары", "Memoirs"), ("Биография", "Biography"), ("Путешествия", "Travel"),
    ("Научная фантастика", "Sci-Fi Books"), ("Детектив", "Mystery"), ("Фэнтези", "Fantasy Books"),
    ("Классика", "Classics"), ("Современная", "Contemporary"), ("Молодёжная", "YA"),
    ("Детская", "Children"), ("Кулинарная", "Cookbook"), ("Учебник", "Textbook"),
    ("Комикс", "Comic"), ("Манга", "Manga"), ("Веб-комикс", "Webcomic"),
    ("Театр", "Theater"), ("Опера", "Opera"), ("Балет", "Ballet"),
    ("Цирк", "Circus"), ("Кабаре", "Cabaret"), ("Варьете", "Variety"),
    ("Выставка", "Exhibition"), ("Фестиваль", "Festival"), ("Концерт", "Concert"),
    ("Вернисаж", "Vernissage"), ("Аукцион", "Auction"), ("Галерея", "Gallery"),
    ("Коллекция", "Collection"), ("Архив", "Archive"), ("Фонд", "Foundation"),
    ("Грант", "Grant"), ("Премия", "Award"), ("Конкурс", "Competition"),
    
    # ⚽ Спорт и активный отдых (100)
    ("Футбол", "Football"), ("Баскетбол", "Basketball"), ("Волейбол", "Volleyball"),
    ("Теннис", "Tennis"), ("Бадминтон", "Badminton"), ("Настольный теннис", "Table Tennis"),
    ("Хоккей", "Hockey"), ("Регби", "Rugby"), ("Американский футбол", "American Football"),
    ("Бейсбол", "Baseball"), ("Крикет", "Cricket"), ("Гандбол", "Handball"),
    ("Бокс", "Boxing"), ("Борьба", "Wrestling"), ("Дзюдо", "Judo"),
    ("Карате", "Karate"), ("Тхэквондо", "Taekwondo"), ("Кикбоксинг", "Kickboxing"),
    ("ММА", "MMA"), ("Фехтование", "Fencing"), ("Стрельба", "Shooting"),
    ("Лёгкая атлетика", "Athletics"), ("Бег", "Running"), ("Марафон", "Marathon"),
    ("Спринт", "Sprint"), ("Барьерный бег", "Hurdles"), ("Эстафета", "Relay"),
    ("Прыжки", "Jumping"), ("Метание", "Throwing"), ("Многоборье", "Decathlon"),
    ("Плавание", "Swimming"), ("Ныряние", "Diving"), ("Водное поло", "Water Polo"),
    ("Синхронное плавание", "Synchronized Swimming"), ("Серфинг", "Surfing"), ("Виндсёрфинг", "Windsurfing"),
    ("Кайтсёрфинг", "Kitesurfing"), ("Вейкбординг", "Wakeboarding"), ("Скаякинг", "Kayaking"),
    ("Рафтинг", "Rafting"), ("Гребля", "Rowing"), ("Парусный спорт", "Sailing"),
    ("Яхтинг", "Yachting"), ("Круизы", "Cruises"), ("Рыбалка", "Fishing"),
    ("Лыжи", "Skiing"), ("Сноуборд", "Snowboarding"), ("Фристайл", "Freestyle"),
    ("Биатлон", "Biathlon"), ("Санный спорт", "Luge"), ("Бобслей", "Bobsleigh"),
    ("Фигурное катание", "Figure Skating"), ("Шорт-трек", "Short Track"), ("Кёрлинг", "Curling"),
    ("Велоспорт", "Cycling"), ("Маунтинбайк", "Mountain Bike"), ("BMX", "BMX"),
    ("Триатлон", "Triathlon"), ("Дуатлон", "Duathlon"), ("Айронмен", "Ironman"),
    ("Альпинизм", "Mountaineering"), ("Скалолазание", "Rock Climbing"), ("Ледолазание", "Ice Climbing"),
    ("Парапланеризм", "Paragliding"), ("Дельтаплан", "Hang Gliding"), ("Прыжки с парашютом", "Skydiving"),
    ("Пейнтбол", "Paintball"), ("Лазертаг", "Laser Tag"), ("Страйкбол", "Airsoft"),
    ("Квест", "Quest"), ("Эскейп-рум", "Escape Room"), ("Настольные игры", "Board Games"),
    ("Шахматы", "Chess"), ("Шашки", "Checkers"), ("Го", "Go"),
    ("Покер", "Poker"), ("Бильярд", "Billiards"), ("Дартс", "Darts"),
    ("Боулинг", "Bowling"), ("Гольф", "Golf"), ("Крокет", "Croquet"),
    ("Йога", "Yoga"), ("Пилатес", "Pilates"), ("Стретчинг", "Stretching"),
    ("Кроссфит", "CrossFit"), ("Фитнес", "Fitness"), ("Бодибилдинг", "Bodybuilding"),
    ("Пауэрлифтинг", "Powerlifting"), ("Гиревой спорт", "Kettlebell"), ("Армрестлинг", "Arm Wrestling"),
    ("Танцы", "Dancing"), ("Сальса", "Salsa"), ("Танго", "Tango"),
    ("Вальс", "Waltz"), ("Хип-хоп танцы", "Hip-hop Dance"), ("Брейк-данс", "Breakdance"),
    ("Спортивные танцы", "Dancesport"), ("Чирлидинг", "Cheerleading"), ("Акробатика", "Acrobatics"),
    ("Гимнастика", "Gymnastics"), ("Аэробика", "Aerobics"), ("Зумба", "Zumba"),
    ("Туризм", "Tourism"), ("Поход", "Hiking"), ("Кемпинг", "Camping"),
    ("Бэкпекинг", "Backpacking"), ("Экотуризм", "Ecotourism"), ("Приключенческий туризм", "Adventure Travel"),
    
    # 🎓 Образование и наука (100)
    ("Математика", "Mathematics"), ("Алгебра", "Algebra"), ("Геометрия", "Geometry"),
    ("Тригонометрия", "Trigonometry"), ("Матанализ", "Calculus"), ("Статистика", "Statistics"),
    ("Физика", "Physics"), ("Механика", "Mechanics"), ("Оптика", "Optics"),
    ("Термодинамика", "Thermodynamics"), ("Электромагнетизм", "Electromagnetism"), ("Квантовая физика", "Quantum Physics"),
    ("Химия", "Chemistry"), ("Органическая", "Organic"), ("Неорганическая", "Inorganic"),
    ("Биохимия", "Biochemistry"), ("Физхимия", "Physical Chemistry"), ("Аналитическая", "Analytical"),
    ("Биология", "Biology"), ("Ботаника", "Botany"), ("Зоология", "Zoology"),
    ("Микробиология", "Microbiology"), ("Генетика", "Genetics"), ("Эволюция", "Evolution"),
    ("Экология", "Ecology"), ("Анатомия", "Anatomy"), ("Физиология", "Physiology"),
    ("Медицина", "Medicine"), ("Терапия", "Therapy"), ("Хирургия", "Surgery"),
    ("Педиатрия", "Pediatrics"), ("Кардиология", "Cardiology"), ("Неврология", "Neurology"),
    ("Психология", "Psychology"), ("Психиатрия", "Psychiatry"), ("Психотерапия", "Psychotherapy"),
    ("Социология", "Sociology"), ("Антропология", "Anthropology"), ("Этнография", "Ethnography"),
    ("История", "History"), ("Археология", "Archaeology"), ("Палеонтология", "Paleontology"),
    ("География", "Geography"), ("Геология", "Geology"), ("Метеорология", "Meteorology"),
    ("Океанология", "Oceanology"), ("Астрономия", "Astronomy"), ("Астрофизика", "Astrophysics"),
    ("Космология", "Cosmology"), ("Философия", "Philosophy"), ("Логика", "Logic"),
    ("Этика", "Ethics"), ("Эстетика", "Aesthetics"), ("Эпистемология", "Epistemology"),
    ("Лингвистика", "Linguistics"), ("Фонетика", "Phonetics"), ("Синтаксис", "Syntax"),
    ("Семантика", "Semantics"), ("Прагматика", "Pragmatics"), ("Перевод", "Translation"),
    ("Филология", "Philology"), ("Литературоведение", "Literary Studies"), ("Искусствоведение", "Art History"),
    ("Экономика", "Economics"), ("Микроэкономика", "Microeconomics"), ("Макроэкономика", "Macroeconomics"),
    ("Финансы", "Finance"), ("Бухгалтерия", "Accounting"), ("Аудит", "Auditing"),
    ("Менеджмент", "Management"), ("Маркетинг", "Marketing"), ("PR", "PR"),
    ("Юриспруденция", "Law"), ("Гражданское право", "Civil Law"), ("Уголовное право", "Criminal Law"),
    ("Международное право", "International Law"), ("Конституционное право", "Constitutional Law"),
    ("Политология", "Political Science"), ("Международные отношения", "International Relations"),
    ("Педагогика", "Pedagogy"), ("Методика", "Methodology"), ("Дидактика", "Didactics"),
    ("Онлайн-обучение", "E-learning"), ("MOOC", "MOOC"), ("Тьюторство", "Tutoring"),
    ("Курсы", "Courses"), ("Тренинги", "Trainings"), ("Вебинары", "Webinars"),
    ("Сертификация", "Certification"), ("Диплом", "Diploma"), ("Степень", "Degree"),
    ("Бакалавр", "Bachelor"), ("Магистр", "Master"), ("Доктор", "PhD"),
    ("Диссертация", "Dissertation"), ("Исследование", "Research"), ("Эксперимент", "Experiment"),
    ("Гипотеза", "Hypothesis"), ("Теория", "Theory"), ("Модель", "Model"),
    ("Алгоритм", "Algorithm"), ("Формула", "Formula"), ("Закон", "Law"),
    ("Принцип", "Principle"), ("Метод", "Method"), ("Техника", "Technique"),
    
    # 🚗 Транспорт и логистика (100)
    ("Автомобиль", "Car"), ("Седан", "Sedan"), ("Хэтчбек", "Hatchback"),
    ("Универсал", "Wagon"), ("Купе", "Coupe"), ("Кабриолет", "Convertible"),
    ("Внедорожник", "SUV"), ("Пикап", "Pickup"), ("Минивэн", "Minivan"),
    ("Спорткар", "Sports Car"), ("Мотоцикл", "Motorcycle"), ("Скутер", "Scooter"),
    ("Мопед", "Moped"), ("Велосипед", "Bicycle"), ("Электросамокат", "E-scooter"),
    ("Грузовик", "Truck"), ("Фургон", "Van"), ("Автобус", "Bus"),
    ("Троллейбус", "Trolleybus"), ("Трамвай", "Tram"), ("Метро", "Metro"),
    ("Поезд", "Train"), ("Электричка", "Commuter Train"), ("Экспресс", "Express"),
    ("Локомотив", "Locomotive"), ("Вагон", "Carriage"), ("Цистерна", "Tank Car"),
    ("Самолёт", "Airplane"), ("Вертолёт", "Helicopter"), ("Дрон", "Drone"),
    ("Планер", "Glider"), ("Параплан", "Paraglider"), ("Дирижабль", "Airship"),
    ("Корабль", "Ship"), ("Лайнер", "Liner"), ("Паром", "Ferry"),
    ("Яхта", "Yacht"), ("Катер", "Motorboat"), ("Лодка", "Boat"),
    ("Парусник", "Sailboat"), ("Подлодка", "Submarine"), ("Ледокол", "Icebreaker"),
    ("Ракета", "Rocket"), ("Спутник", "Satellite"), ("Станция", "Space Station"),
    ("Марсоход", "Rover"), ("Зонд", "Probe"), ("Телескоп", "Telescope"),
    ("Такси", "Taxi"), ("Каршеринг", "Carsharing"), ("Прокат", "Rental"),
    ("Доставка", "Delivery"), ("Курьер", "Courier"), ("Почта", "Mail"),
    ("Логистика", "Logistics"), ("Склад", "Warehouse"), ("Дистрибуция", "Distribution"),
    ("Цепочка поставок", "Supply Chain"), ("Инвентаризация", "Inventory"), ("Фулфилмент", "Fulfillment"),
    ("Экспорт", "Export"), ("Импорт", "Import"), ("Таможня", "Customs"),
    ("Контейнер", "Container"), ("Паллет", "Pallet"), ("Упаковка", "Packaging"),
    ("Топливо", "Fuel"), ("Бензин", "Gasoline"), ("Дизель", "Diesel"),
    ("Электричество", "Electricity"), ("Гибрид", "Hybrid"), ("Водород", "Hydrogen"),
    ("Аккумулятор", "Battery"), ("Зарядка", "Charging"), ("Станция подзарядки", "Charging Station"),
    ("Двигатель", "Engine"), ("Трансмиссия", "Transmission"), ("Подвеска", "Suspension"),
    ("Тормоза", "Brakes"), ("Рулевое", "Steering"), ("Шины", "Tires"),
    ("Навигация", "Navigation"), ("GPS", "GPS"), ("Радар", "Radar"),
    ("Автопилот", "Autopilot"), ("Беспилотник", "Self-driving"), ("ADAS", "ADAS"),
    ("ДТП", "Accident"), ("Страховка", "Insurance"), ("ТО", "Maintenance"),
    ("Диагностика", "Diagnostics"), ("Ремонт", "Repair"), ("Тюнинг", "Tuning"),
    ("Дорога", "Road"), ("Шоссе", "Highway"), ("Магистраль", "Motorway"),
    ("Развязка", "Interchange"), ("Эстакада", "Overpass"), ("Тоннель", "Tunnel"),
    ("Светофор", "Traffic Light"), ("Знак", "Sign"), ("Разметка", "Marking"),
    ("Парковка", "Parking"), ("Заправка", "Gas Station"), ("Шиномонтаж", "Tire Service"),
    ("Автосервис", "Auto Service"), ("Мойка", "Car Wash"), ("Детейлинг", "Detailing"),
    ("Права", "License"), ("ПДД", "Traffic Rules"), ("Экзамен", "Driving Test"),
    
    # 🏠 Дом и быт (100)
    ("Диван", "Sofa"), ("Кресло", "Armchair"), ("Стул", "Chair"),
    ("Стол", "Table"), ("Кровать", "Bed"), ("Шкаф", "Wardrobe"),
    ("Комод", "Chest of Drawers"), ("Тумба", "Nightstand"), ("Полка", "Shelf"),
    ("Стеллаж", "Rack"), ("Вешалка", "Coat Rack"), ("Зеркало", "Mirror"),
    ("Ковер", "Carpet"), ("Шторы", "Curtains"), ("Жалюзи", "Blinds"),
    ("Люстра", "Chandelier"), ("Лампа", "Lamp"), ("Светильник", "Light Fixture"),
    ("Холодильник", "Refrigerator"), ("Морозилка", "Freezer"), ("Плита", "Stove"),
    ("Духовка", "Oven"), ("Микроволновка", "Microwave"), ("Посудомойка", "Dishwasher"),
    ("Стиралка", "Washing Machine"), ("Сушилка", "Dryer"), ("Утюг", "Iron"),
    ("Пылесос", "Vacuum"), ("Робот-пылесос", "Robot Vacuum"), ("Кондиционер", "AC"),
    ("Обогреватель", "Heater"), ("Вентилятор", "Fan"), ("Увлажнитель", "Humidifier"),
    ("Телевизор", "TV"), ("Проектор", "Projector"), ("Аудиосистема", "Audio System"),
    ("Колонки", "Speakers"), ("Наушники", "Headphones"), ("Микрофон", "Microphone"),
    ("Компьютер", "Computer"), ("Ноутбук", "Laptop"), ("Планшет", "Tablet"),
    ("Смартфон", "Smartphone"), ("Умные часы", "Smartwatch"), ("Фитнес-браслет", "Fitness Tracker"),
    ("Камера", "Camera"), ("Дрон", "Drone"), ("Экшн-камера", "Action Camera"),
    ("Принтер", "Printer"), ("Сканер", "Scanner"), ("Роутер", "Router"),
    ("Модем", "Modem"), ("Wi-Fi", "Wi-Fi"), ("Bluetooth", "Bluetooth"),
    ("Умный дом", "Smart Home"), ("Датчик", "Sensor"), ("Камера наблюдения", "Security Camera"),
    ("Домофон", "Intercom"), ("Замок", "Smart Lock"), ("Сигнализация", "Alarm"),
    ("Посуда", "Tableware"), ("Тарелка", "Plate"), ("Чашка", "Cup"),
    ("Ложка", "Spoon"), ("Вилка", "Fork"), ("Нож", "Knife"),
    ("Кастрюля", "Pot"), ("Сковорода", "Pan"), ("Чайник", "Kettle"),
    ("Текстиль", "Textiles"), ("Постельное бельё", "Bedding"), ("Полотенца", "Towels"),
    ("Плед", "Blanket"), ("Подушка", "Pillow"), ("Одеяло", "Duvet"),
    ("Декор", "Decor"), ("Ваза", "Vase"), ("Свеча", "Candle"),
    ("Рамка", "Frame"), ("Статуэтка", "Figurine"), ("Часы", "Clock"),
    ("Растение", "Plant"), ("Цветочный горшок", "Planter"), ("Удобрение", "Fertilizer"),
    ("Инструменты", "Tools"), ("Молоток", "Hammer"), ("Отвёртка", "Screwdriver"),
    ("Дрель", "Drill"), ("Пила", "Saw"), ("Рулетка", "Tape Measure"),
    ("Ключ", "Wrench"), ("Плоскогубцы", "Pliers"), ("Уровень", "Level"),
    ("Краска", "Paint"), ("Кисть", "Brush"), ("Валик", "Roller"),
    ("Обои", "Wallpaper"), ("Плитка", "Tiles"), ("Ламинат", "Laminate"),
    ("Паркет", "Parquet"), ("Линолеум", "Linoleum"), ("Натяжной потолок", "Stretch Ceiling"),
    ("Сантехника", "Plumbing"), ("Кран", "Faucet"), ("Смеситель", "Mixer"),
    ("Унитаз", "Toilet"), ("Раковина", "Sink"), ("Ванна", "Bathtub"),
    ("Душ", "Shower"), ("Кабина", "Shower Cabin"), ("Бойлер", "Water Heater"),
    ("Электрика", "Electrical"), ("Розетка", "Outlet"), ("Выключатель", "Switch"),
    ("Проводка", "Wiring"), ("Автомат", "Circuit Breaker"), ("Щиток", "Electrical Panel"),
    
    # 🎁 Разное (100)
    ("Подарок", "Gift"), ("Сюрприз", "Surprise"), ("Открытка", "Card"),
    ("Упаковка", "Gift Wrap"), ("Лента", "Ribbon"), ("Бант", "Bow"),
    ("Праздник", "Holiday"), ("День рождения", "Birthday"), ("Свадьба", "Wedding"),
    ("Юбилей", "Anniversary"), ("Новый год", "New Year"), ("Рождество", "Christmas"),
    ("Пасха", "Easter"), ("Хэллоуин", "Halloween"), ("День святого Валентина", "Valentine's Day"),
    ("8 марта", "Women's Day"), ("23 февраля", "Defender's Day"), ("1 мая", "Labor Day"),
    ("9 мая", "Victory Day"), ("Выпускной", "Graduation"), ("Корпоратив", "Corporate Event"),
    ("Фуршет", "Buffet"), ("Банкет", "Banquet"), ("Пикник", "Picnic"),
    ("Барбекю", "BBQ"), ("Шашлыки", "Grilling"), ("Костёр", "Bonfire"),
    ("Палатка", "Tent"), ("Спальник", "Sleeping Bag"), ("Рюкзак", "Backpack"),
    ("Фонарь", "Flashlight"), ("Компас", "Compass"), ("Карта", "Map"),
    ("Бинокль", "Binoculars"), ("Фотоаппарат", "Camera"), ("Штатив", "Tripod"),
    ("Краски", "Paints"), ("Кисти", "Brushes"), ("Холст", "Canvas"),
    ("Бумага", "Paper"), ("Блокнот", "Notebook"), ("Ручка", "Pen"),
    ("Карандаш", "Pencil"), ("Маркер", "Marker"), ("Ластик", "Eraser"),
    ("Ножницы", "Scissors"), ("Клей", "Glue"), ("Скотч", "Tape"),
    ("Конверт", "Envelope"), ("Марка", "Stamp"), ("Посылка", "Parcel"),
    ("Ключи", "Keys"), ("Кошелёк", "Wallet"), ("Сумка", "Bag"),
    ("Рюкзак", "Backpack"), ("Чемодан", "Suitcase"), ("Дорожная сумка", "Duffel"),
    ("Одежда", "Clothing"), ("Футболка", "T-shirt"), ("Рубашка", "Shirt"),
    ("Джинсы", "Jeans"), ("Брюки", "Pants"), ("Шорты", "Shorts"),
    ("Платье", "Dress"), ("Юбка", "Skirt"), ("Костюм", "Suit"),
    ("Пиджак", "Blazer"), ("Куртка", "Jacket"), ("Пальто", "Coat"),
    ("Свитер", "Sweater"), ("Худи", "Hoodie"), ("Толстовка", "Sweatshirt"),
    ("Нижнее бельё", "Underwear"), ("Носки", "Socks"), ("Колготки", "Tights"),
    ("Обувь", "Footwear"), ("Кроссовки", "Sneakers"), ("Ботинки", "Boots"),
    ("Туфли", "Shoes"), ("Сандалии", "Sandals"), ("Тапочки", "Slippers"),
    ("Шапка", "Hat"), ("Кепка", "Cap"), ("Шарф", "Scarf"),
    ("Перчатки", "Gloves"), ("Ремень", "Belt"), ("Галстук", "Tie"),
    ("Украшения", "Jewelry"), ("Кольцо", "Ring"), ("Серьги", "Earrings"),
    ("Цепочка", "Chain"), ("Браслет", "Bracelet"), ("Часы", "Watch"),
    ("Очки", "Glasses"), ("Солнцезащитные", "Sunglasses"), ("Контактные линзы", "Contact Lenses"),
    ("Косметика", "Cosmetics"), ("Помада", "Lipstick"), ("Тушь", "Mascara"),
    ("Тональный крем", "Foundation"), ("Пудра", "Powder"), ("Румяна", "Blush"),
    ("Тени", "Eyeshadow"), ("Подводка", "Eyeliner"), ("Лак для ногтей", "Nail Polish"),
    ("Парфюм", "Perfume"), ("Дезодорант", "Deodorant"), ("Лосьон", "Lotion"),
    ("Шампунь", "Shampoo"), ("Кондиционер", "Conditioner"), ("Мыло", "Soap"),
    ("Зубная паста", "Toothpaste"), ("Щётка", "Toothbrush"), ("Нить", "Dental Floss"),
    ("Бритва", "Razor"), ("Триммер", "Trimmer"), ("Фен", "Hair Dryer"),
    ("Плойка", "Curling Iron"), ("Выпрямитель", "Straightener"), ("Расчёска", "Comb"),
]


class Command(BaseCommand):
    """
    Команда для генерации 1000 тестовых категорий.
    
    Использование:
        python manage.py seed_categories              # Добавить категории
        python manage.py seed_categories --clear      # Очистить и добавить заново
        python manage.py seed_categories --dry-run    # Показать, что будет сделано, без изменений
    """
    
    help = 'Генерирует 1000 разнообразных категорий для тестирования'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить существующие категории перед генерацией'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Показать план действий без внесения изменений'
        )
    
    def handle(self, *args, **options):
        clear = options['clear']
        dry_run = options['dry_run']
        
        self.stdout.write(self.style.SUCCESS(f'📦 Загружено {len(CATEGORIES_DATASET)} категорий для генерации'))
        
        # Проверка на дубликаты в датасете
        names_ru = [name_ru for name_ru, _ in CATEGORIES_DATASET]
        if len(names_ru) != len(set(names_ru)):
            self.stdout.write(self.style.WARNING('⚠️  В датасете есть дубликаты названий на русском'))
        
        # Опция очистки
        if clear:
            if dry_run:
                self.stdout.write(f'🗑️  [DRY RUN] Будет удалено {Category.objects.count()} существующих категорий')
            else:
                count = Category.objects.count()
                Category.objects.all().delete()
                logger.info(f"Очищено {count} категорий (clear mode)")
                self.stdout.write(self.style.SUCCESS(f'🗑️  Удалено {count} существующих категорий'))
        
        # Подсчёт новых категорий
        existing_names = set(Category.objects.values_list('name_ru', flat=True))
        new_categories = [
            (ru, en) for ru, en in CATEGORIES_DATASET 
            if ru not in existing_names
        ]
        
        self.stdout.write(f'📊 Найдено {len(new_categories)} новых категорий для добавления')
        self.stdout.write(f'📊 Пропущено {len(CATEGORIES_DATASET) - len(new_categories)} уже существующих')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY RUN: Изменения не будут внесены'))
            if new_categories[:5]:
                self.stdout.write('Примеры категорий для добавления:')
                for ru, en in new_categories[:5]:
                    self.stdout.write(f'  • {ru} / {en}')
            return
        
        # Массовое создание с логированием прогресса
        if new_categories:
            with transaction.atomic():
                categories_to_create = []
                for i, (name_ru, name_en) in enumerate(new_categories, 1):
                    categories_to_create.append(
                        Category(name_ru=name_ru, name_en=name_en)
                    )
                    # Логирование прогресса каждые 100 записей
                    if i % 100 == 0:
                        logger.info(f"Подготовлено {i}/{len(new_categories)} категорий")
                        self.stdout.write(f'⏳ Подготовлено {i}/{len(new_categories)}...')
                
                Category.objects.bulk_create(categories_to_create, ignore_conflicts=True)
                logger.info(f"Создано {len(categories_to_create)} категорий")
                self.stdout.write(self.style.SUCCESS(f'✅ Создано {len(categories_to_create)} категорий'))
        else:
            self.stdout.write(self.style.WARNING('⚠️  Нет новых категорий для добавления'))
        
        # Итоговая статистика
        total = Category.objects.count()
        self.stdout.write(self.style.SUCCESS(f'🎉 Всего категорий в базе: {total}'))
        logger.info(f"Команда завершена. Всего категорий: {total}")