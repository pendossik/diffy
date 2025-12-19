import "./body.css";
import Search from "./Search";
import { useState } from "react";
import ShortCompareCard from "./ShortCompareCard";
import { useNavigate } from "react-router-dom";
import axios from "axios";

export function HomePage() {
  const [firstProduct, setFirstProduct] = useState({ id: 0, name: "" });
  const [secondProduct, setSecondProduct] = useState({ id: 0, name: "" });
  const [compareData, setCompareData] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleCompare = () => {
    if (firstProduct.id === secondProduct.id) {
      setError("Товары должны быть разными");
      return;
    }

    axios
      .post(`${import.meta.env.VITE_API_URL}/compare/comparetest/`, {
        product1: firstProduct.id,
        product2: secondProduct.id,
      })
      .then((res) => {
        console.log("RESPONSE:", res.data);
        setCompareData(res.data);
      })
      .catch(() => setError("Ошибка загрузки данных"));
  };

  return (
    <main>
      <div className="search-block">
        <div className="search-compare">
          <Search
            text="Название первого товара"
            value={firstProduct.name}
            onChange={(id, name) => setFirstProduct({ id, name })}
          />
          <img src="./src/icons/Plus.svg" alt="image plus" width="70" />
          <Search
            text="Название второго товара"
            value={secondProduct.name}
            onChange={(id, name) => setSecondProduct({ id, name })}
          />
        </div>

        <div className="compare-button">
          <button
            disabled={!firstProduct.id || !secondProduct.id}
            onClick={handleCompare}
          >
            Сравнить
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="cards-bg">
        {compareData && compareData.length >= 2 && (
          <div>
            <div className="compare">
              <ShortCompareCard data={compareData[0]} bg="short-product1" />
              <ShortCompareCard data={compareData[1]} bg="short-product2" />
            </div>

            <button
              className="more-btn"
              onClick={() =>
                navigate("/compare", {
                  state: {
                    firstData: compareData[0],
                    secondData: compareData[1],
                  },
                })
              }
            >
              Подробнее
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
