import "./full-card.css";
import { useState } from "react";
import { useLocation } from "react-router-dom";
import favOff from "../../icons/Favourite_button.svg";
import favOn from "../../icons/Favourite_button_active.svg";

type Char = {
  id: number;
  name: string;
  value: string;
};

type CharGroup = {
  name: string;
  characteristics: Char[];
};

type Product = {
  id: number;
  name: string;
  img: string | null;
  characteristics_groups: CharGroup[];
};

export function FullCompareCard() {
  const { state } = useLocation();
  const products: Product[] = state?.products || [];

  const [isFav, setIsFav] = useState(false);

  if (!products.length) {
    return (
      <p style={{ color: "white", textAlign: "center" }}>
        Нет данных для сравнения
      </p>
    );
  }

  const getChar = (product: Product, charName: string) => {
    for (const group of product.characteristics_groups) {
      const found = group.characteristics.find((c) => c.name === charName);
      if (found) return found.value;
    }
    return "-";
  };

  function parseValue(str: string): number | null {
    if (!str) return null;
    const n = parseFloat(str.replace(",", "."));
    return isNaN(n) ? null : n;
  }

  function getBestWorst(products: Product[], field: string) {
    const list = products.map((p) => {
      const raw = getChar(p, field);
      const num = parseValue(raw);
      return { id: p.id, raw, num };
    });

    const numeric = list.filter((v) => v.num !== null);
    if (!numeric.length) return { maxIds: [], minIds: [] };

    const max = Math.max(...numeric.map((v) => v.num!));
    const min = Math.min(...numeric.map((v) => v.num!));

    return {
      maxIds: numeric.filter((v) => v.num === max).map((v) => v.id),
      minIds: numeric.filter((v) => v.num === min).map((v) => v.id),
    };
  }

  const sections = [
    { title: "Размеры", fields: ["Ширина", "Высота", "Толщина", "Вес"] },
    {
      title: "Корпус",
      fields: ["Материал задней панели", "Материал граней", "Пыле-влагозащита"],
    },
    {
      title: "Дисплей",
      fields: [
        "Тип экрана",
        "Диагональ экрана",
        "Разрешение экрана",
        "Частота экрана",
        "Яркость экрана",
        "Плотность пикселей",
        "Соотношение сторон",
      ],
    },
    { title: "Процессор", fields: ["Модель процессора", "Количество ядер"] },
    { title: "Батарея", fields: ["Аккумулятор"] },
    {
      title: "Основная камера",
      fields: ["Количество камер", "Количество мегапикселей"],
    },
    { title: "Фронтальная камера", fields: ["Фронтальная камера"] },
    { title: "Операционная система", fields: ["Операционная система"] },
    { title: "Bluetooth", fields: ["Bluetooth"] },
  ];

  return (
    <main className="compare-page">
      {/* Верх */}
      <div className="cards">
        <div className="description">
          {products.map((p, i) => (
            <div key={p.id} className={`product product${i + 1}`}>
              <div className="card-image-wrapper">
                {p.img ? (
                  <img src={p.img} alt={p.name} className="card-image" />
                ) : (
                  <div className="image-placeholder" />
                )}
              </div>
              <p>{p.name}</p>
            </div>
          ))}
        </div>

        {/* <button className="fav-btn" onClick={() => setIsFav(!isFav)}>
          <img src={isFav ? favOn : favOff} alt="fav" />
        </button> */}
      </div>

      {/* Таблица */}
      <div className="full">
        <div className="full-card">
          {sections.map((section) => (
            <div key={section.title}>
              <div className="main-char-header">
                <h2>{section.title}</h2>
              </div>

              {section.fields.map((field) => {
                const { maxIds, minIds } = getBestWorst(products, field);

                return (
                  <div key={field}>
                    <h4 className="char-header">{field}</h4>
                    <div className="char">
                      {products.map((p) => {
                        const value = getChar(p, field);
                        const className = maxIds.includes(p.id)
                          ? "best"
                          : minIds.includes(p.id)
                            ? "worst"
                            : "";

                        return (
                          <p key={p.id} className={className}>
                            {value}
                          </p>
                        );
                      })}
                    </div>
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
