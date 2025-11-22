import "./phone-cards.css";
import { useState } from "react";
import { useLocation } from "react-router-dom";
import Records from "../../records.json";
import favOff from "../../icons/Favourite_button.svg";
import favOn from "../../icons/Favourite_button_active.svg";

export function PhoneCards() {
  const { state } = useLocation();
  const { firstProduct, secondProduct } = state;
  const firstProductData = Records.find(
    (record) => record.name === firstProduct
  );
  const secondProductData = Records.find(
    (record) => record.name === secondProduct
  );

  const [isFav, setIsFav] = useState(false);

  return (
    <main>
      <div className="cards">
        <div className="description">
          <div className="product1">
            <img className="card" src={firstProductData?.img} alt={firstProductData?.name} />
            <p>{firstProductData?.name}</p>
          </div>
          <div className="product2">
            <img className="card" src={secondProductData?.img} alt={secondProductData?.name} />
            <p>{secondProductData?.name}</p>
          </div>
        </div>
        <button className="fav-btn" onClick={() => setIsFav(!isFav)}>
          <img src={isFav ? favOn : favOff} alt="favourite icon" />
        </button>
      </div>

      <div className="full-card">

        <h4 className="char-header">Год релиза</h4>
        <div className="char">
          <p>{firstProductData?.["release-date"]}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.["release-date"]}</p>
        </div>

        
      <div className="main-char-header">
          <h2>Размеры</h2>
        </div>
        <h4 className="char-header">Ширина</h4>
        <div className="char">
          <p>{firstProductData?.size?.width}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.size?.width}</p>
        </div>
        <h4 className="char-header">Высота</h4>
        <div className="char">
          <p>{firstProductData?.size?.height}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.size?.height}</p>
        </div>
        <h4 className="char-header">Толщина</h4>
        <div className="char">
          <p>{firstProductData?.size?.thickness}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.size?.thickness}</p>
        </div>
        <h4 className="char-header">Вес</h4>
        <div className="char">
          <p>{firstProductData?.weight}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.weight}</p>
        </div>

<div className="main-char-header">
          <h2>Корпус</h2>
        </div>
        <h4 className="char-header">Материал задней панели</h4>
        <div className="char">
          <p>{firstProductData?.body?.back}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.body?.back}</p>
        </div>
        <h4 className="char-header">Материал граней</h4>
        <div className="char">
          <p>{firstProductData?.body?.edges}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.body?.edges}</p>
        </div>
        <h4 className="char-header">Степень защиты IP</h4>
        <div className="char">
          <p>{firstProductData?.body?.ip}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.body?.ip}</p>
        </div>

        <div className="main-char-header">
          <h2>Дисплей</h2>
        </div>
        <h4 className="char-header">Тип матрицы</h4>
        <div className="char">
          <p>{firstProductData?.display.type}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.type}</p>
        </div>
        <h4 className="char-header">Размер</h4>
        <div className="char">
          <p>{firstProductData?.display.size}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.size}</p>
        </div>
        <h4 className="char-header">Разрешение</h4>
        <div className="char">
          <p>{firstProductData?.display.resolution}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.resolution}</p>
        </div>
        <h4 className="char-header">Частота</h4>
        <div className="char">
          <p>{firstProductData?.display.frequency}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.frequency}</p>
        </div>
        <h4 className="char-header">Яркость</h4>
        <div className="char">
          <p>{firstProductData?.display.brightness}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.brightness}</p>
        </div>
        <h4 className="char-header">Плотность пикселей</h4>
        <div className="char">
          <p>{firstProductData?.display.ppi}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display.ppi}</p>
        </div>
        <h4 className="char-header">Соотношение сторон</h4>
        <div className="char">
          <p>{firstProductData?.display["aspect-ratio"]}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.display["aspect-ratio"]}</p>
        </div>


      <div className="main-char-header">
          <h2>Процессор</h2>
        </div>
        <h4 className="char-header">Модель процессора</h4>
        <div className="char">
          <p>{firstProductData?.cpu?.model}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.cpu?.model}</p>
        </div>
        <h4 className="char-header">Количество ядер</h4>
        <div className="char">
          <p>{firstProductData?.cpu?.cores}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.cpu?.cores}</p>
        </div>
        <div className="main-char-header">
          <h2>Батарея</h2>
        </div>
        <h4 className="char-header">Емкость батареи</h4>
         <div className="char">
          <p>{firstProductData?.battery}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.battery}</p>
        </div>

        <div className="main-char-header">
          <h2>Основная камера</h2>
        </div>
        <h4 className="char-header">Количество камер</h4>
         <div className="char">
          <p>{firstProductData?.camera?.amount}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.camera?.amount}</p>
        </div>
        <h4 className="char-header">Количество мегапикселей</h4>
         <div className="char">
          <p>{firstProductData?.camera?.mp}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.camera?.mp}</p>
        </div>
        <h4 className="char-header">Тип модулей камеры</h4>
         <div className="char">
          <p>{firstProductData?.camera?.type}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.camera?.type}</p>
        </div>

        <div className="main-char-header">
          <h2>Фронтальная камера</h2>
        </div>
        <h4 className="char-header">Количество мегапикселей</h4>
         <div className="char">
          <p>{firstProductData?.["frontal-camera"]?.mp}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.["frontal-camera"]?.mp}</p>
        </div>

        <div className="main-char-header">
          <h2>Операционная система</h2>
        </div>
         <div className="char">
          <p>{firstProductData?.os}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.os}</p>
        </div>

        <div className="main-char-header">
          <h2>Bluetooth</h2>
        </div>
        <h4 className="char-header">Версия bluetooth</h4>
         <div className="char">
          <p>{firstProductData?.bluetooth}</p>
          <div className="vertical-line"></div>
          <p>{secondProductData?.bluetooth}</p>
        </div>
      </div>
    </main>
  );
}
