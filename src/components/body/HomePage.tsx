import "./body.css";
import Search from "./Search";
import { useState } from "react";
import ShortCompareCard from "./ShortCompareCard";
import { useNavigate } from "react-router-dom";
import axios from "axios";

type CompareResponse = {
  product1: any;
  product2: any;
  product3: any;
};

export function HomePage() {
  const [firstProduct, setFirstProduct] = useState<{
    id: number;
    name: string;
  }>({
    id: 0,
    name: "",
  });

  const [secondProduct, setSecondProduct] = useState<{
    id: number;
    name: string;
  }>({
    id: 0,
    name: "",
  });

  const [thirdProduct, setThirdProduct] = useState<{
    id: number;
    name: string;
  }>({
    id: 0,
    name: "",
  });

  const [compareData, setCompareData] = useState<CompareResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleCompare = () => {
    const ids = [firstProduct.id, secondProduct.id, thirdProduct.id];
    const uniqueIds = new Set(ids);

    if (uniqueIds.size !== 3) {
      setError("Товары должны быть разными");
      return;
    }

    axios
      .post<CompareResponse>("http://127.0.0.1:8000/compare/", {
        product1: firstProduct.id,
        product2: secondProduct.id,
        product3: thirdProduct.id,
      })
      .then((res) => setCompareData(res.data))
      .catch((err) => setError("Ошибка загрузки данных"));
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

          <img src="./src/icons/Plus.svg" alt="image plus" width="70" />

          <Search
            text="Название третьего товара"
            value={thirdProduct.name}
            onChange={(id, name) => setThirdProduct({ id, name })}
          />
        </div>

        <div className="compare-button">
          <button
            disabled={!firstProduct.id && !secondProduct.id && !thirdProduct.id}
            onClick={handleCompare}
          >
            Сравнить
          </button>
        </div>

        {error && <p className="error-text">{error}</p>}
      </div>

      <div className="cards-bg">
        {compareData && (
          <div>
            <div className="compare">
              <ShortCompareCard
                data={compareData.product1}
                bg="short-product1"
              />
              <ShortCompareCard
                data={compareData.product2}
                bg="short-product2"
              />
              <ShortCompareCard
                data={compareData.product3}
                bg="short-product2"
              />
            </div>

            <button
              className="more-btn"
              onClick={() =>
                navigate("/compare", {
                  state: {
                    firstData: compareData.product1,
                    secondData: compareData.product2,
                    thirdData: compareData.product3,
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
