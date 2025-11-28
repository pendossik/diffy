import "./phone-cards.css";
import { useState } from "react";
import { useLocation } from "react-router-dom";
import favOff from "../../icons/Favourite_button.svg";
import favOn from "../../icons/Favourite_button_active.svg";

type Characteristics = {
  id: number;
  name: string;
  value: string;
};

type Product = {
  id: number;
  name: string;
  category: {
    id: number;
    name: string;
  };
  characteristics: Characteristics[];
};

export function PhoneCards() {
  const { state } = useLocation();
  const { firstData, secondData } = state;

  const [isFav, setIsFav] = useState(false);

  // Функция для получения значения характеристики по названию
  const getChar = (product: Product, name: string) => {
    return product?.characteristics?.find((c) => c.name === name)?.value || "-";
  };

  return (
    <main>
      <div className="cards">
        <div className="description">
          <div className="product1">
            <img
              className="card"
              src={getChar(firstData, "Фото")}
              alt={firstData?.name}
            />
            <p>{firstData?.name}</p>
          </div>

          <div className="product2">
            <img
              className="card"
              src={getChar(secondData, "Фото")}
              alt={secondData?.name}
            />
            <p>{secondData?.name}</p>
          </div>
        </div>

        <button className="fav-btn" onClick={() => setIsFav(!isFav)}>
          <img src={isFav ? favOn : favOff} alt="favourite icon" />
        </button>
      </div>

      <div className="full-card">
        {/* --- ГОД РЕЛИЗА --- */}
        <h4 className="char-header">Год релиза</h4>
        <div className="char">
          <p>{firstData?.release_date}</p>
          <div className="vertical-line"></div>
          <p>{secondData?.release_date}</p>
        </div>

        {/* --- РАЗМЕРЫ --- */}
        <div className="main-char-header">
          <h2>Размеры</h2>
        </div>

        <h4 className="char-header">Ширина</h4>
        <div className="char">
          <p>{getChar(firstData, "Ширина")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Ширина")}</p>
        </div>

        <h4 className="char-header">Высота</h4>
        <div className="char">
          <p>{getChar(firstData, "Высота")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Высота")}</p>
        </div>

        <h4 className="char-header">Толщина</h4>
        <div className="char">
          <p>{getChar(firstData, "Толщина")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Толщина")}</p>
        </div>

        <h4 className="char-header">Вес</h4>
        <div className="char">
          <p>{getChar(firstData, "Вес")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Вес")}</p>
        </div>

        {/* --- КОРПУС --- */}
        <div className="main-char-header">
          <h2>Корпус</h2>
        </div>

        <h4 className="char-header">Материал задней панели</h4>
        <div className="char">
          <p>{getChar(firstData, "Материал задней панели")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Материал задней панели")}</p>
        </div>

        <h4 className="char-header">Материал граней</h4>
        <div className="char">
          <p>{getChar(firstData, "Материал граней")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Материал граней")}</p>
        </div>

        <h4 className="char-header">Пыле-влагозащита</h4>
        <div className="char">
          <p>{getChar(firstData, "Пыле-влагозащита")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Пыле-влагозащита")}</p>
        </div>

        {/* --- ДИСПЛЕЙ --- */}
        <div className="main-char-header">
          <h2>Дисплей</h2>
        </div>

        <h4 className="char-header">Тип экрана</h4>
        <div className="char">
          <p>{getChar(firstData, "Тип экрана")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Тип экрана")}</p>
        </div>

        <h4 className="char-header">Диагональ экрана</h4>
        <div className="char">
          <p>{getChar(firstData, "Диагональ экрана")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Диагональ экрана")}</p>
        </div>

        <h4 className="char-header">Разрешение экрана</h4>
        <div className="char">
          <p>{getChar(firstData, "Разрешение экрана")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Разрешение экрана")}</p>
        </div>

        <h4 className="char-header">Частота экрана</h4>
        <div className="char">
          <p>{getChar(firstData, "Частота экрана")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Частота экрана")}</p>
        </div>

        <h4 className="char-header">Яркость экрана</h4>
        <div className="char">
          <p>{getChar(firstData, "Яркость экрана")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Яркость экрана")}</p>
        </div>

        <h4 className="char-header">Плотность пикселей</h4>
        <div className="char">
          <p>{getChar(firstData, "Плотность пикселей")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Плотность пикселей")}</p>
        </div>

        <h4 className="char-header">Соотношение сторон</h4>
        <div className="char">
          <p>{getChar(firstData, "Соотношение сторон")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Соотношение сторон")}</p>
        </div>

        {/* --- ПРОЦЕССОР --- */}
        <div className="main-char-header">
          <h2>Процессор</h2>
        </div>

        <h4 className="char-header">Модель процессора</h4>
        <div className="char">
          <p>{getChar(firstData, "Модель процессора")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Модель процессора")}</p>
        </div>

        <h4 className="char-header">Количество ядер</h4>
        <div className="char">
          <p>{getChar(firstData, "Количество ядер")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Количество ядер")}</p>
        </div>

        {/* --- БАТАРЕЯ --- */}
        <div className="main-char-header">
          <h2>Батарея</h2>
        </div>

        <h4 className="char-header">Аккумулятор</h4>
        <div className="char">
          <p>{getChar(firstData, "Аккумулятор")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Аккумулятор")}</p>
        </div>

        {/* --- ОСНОВНАЯ КАМЕРА --- */}
        <div className="main-char-header">
          <h2>Основная камера</h2>
        </div>

        <h4 className="char-header">Количество камер</h4>
        <div className="char">
          <p>{getChar(firstData, "Количество камер")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Количество камер")}</p>
        </div>

        <h4 className="char-header">Количество мегапикселей</h4>
        <div className="char">
          <p>{getChar(firstData, "Количество мегапикселей")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Количество мегапикселей")}</p>
        </div>

        <h4 className="char-header">Тип задней камеры</h4>
        <div className="char">
          <p>{getChar(firstData, "Тип задней камеры")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Тип задней камеры")}</p>
        </div>

        {/* --- ФРОНТАЛКА --- */}
        <div className="main-char-header">
          <h2>Фронтальная камера</h2>
        </div>
        <h4 className="char-header">Фронтальная камера</h4>
        <div className="char">
          <p>{getChar(firstData, "Фронтальная камера")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Фронтальная камера")}</p>
        </div>

        {/* --- ОС --- */}
        <div className="main-char-header">
          <h2>Операционная система</h2>
        </div>
        <div className="char">
          <p>{getChar(firstData, "Операционная система")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Операционная система")}</p>
        </div>

        {/* --- BLUETOOTH --- */}
        <div className="main-char-header">
          <h2>Bluetooth</h2>
        </div>
        <h4 className="char-header">Версия bluetooth</h4>
        <div className="char">
          <p>{getChar(firstData, "Bluetooth")}</p>
          <div className="vertical-line"></div>
          <p>{getChar(secondData, "Bluetooth")}</p>
        </div>
      </div>
    </main>
  );
}
