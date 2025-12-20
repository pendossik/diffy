import "./body.css";
import Search from "./Search";
import { useState } from "react";
import ShortCompareCard from "./ShortCompareCard";
import { useNavigate } from "react-router-dom";
import axios from "axios";

type Product = {
  id: number;
  name: string;
};

export function HomePage() {
  const [products, setProducts] = useState<Product[]>([
    { id: 0, name: "" }, // first
    { id: 0, name: "" }, // second
    { id: 0, name: "" }, // third
  ]);

  const [compareData, setCompareData] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const updateProduct = (index: number, id: number, name: string) => {
    const updated = [...products];
    updated[index] = { id, name };
    setProducts(updated);
  };

  const selectedProducts = products.filter((p) => p.id !== 0);

  const hasDuplicates =
    new Set(selectedProducts.map((p) => p.id)).size !== selectedProducts.length;

  const handleCompare = () => {
    setError(null);

    if (selectedProducts.length === 0) {
      setError("Выберите хотя бы один товар");
      return;
    }

    if (hasDuplicates) {
      setError("Товары должны быть разными");
      return;
    }

    axios
      .post(`${import.meta.env.VITE_API_URL}/api/compare/comparetest/`, {
        product_ids: selectedProducts.map((p) => p.id),
      })
      .then((res) => {
        console.log("RESPONSE:", res.data);
        setCompareData(res.data);
      })
      .catch(() => setError("Ошибка загрузки данных"));
  };

  return (
    <main>
      <div className="search-section">
        <div className="search-container">
          <div className="search-inputs">
            {/* 1 товар — всегда */}
            <Search
              text="Название первого товара"
              value={products[0].name}
              onChange={(id, name) => updateProduct(0, id, name)}
            />

            {/* 2 товар — появляется после выбора первого */}
            {products[0].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src="./src/icons/Plus.svg" alt="plus" width="70" />
                </div>
                <Search
                  text="Название второго товара"
                  value={products[1].name}
                  onChange={(id, name) => updateProduct(1, id, name)}
                />
              </>
            )}

            {/* 3 товар — появляется после выбора второго */}
            {products[1].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src="./src/icons/Plus.svg" alt="plus" width="70" />
                </div>
                <Search
                  text="Название третьего товара"
                  value={products[2].name}
                  onChange={(id, name) => updateProduct(2, id, name)}
                />
              </>
            )}
          </div>

          <div className="compare-button-wrapper">
            <button
              className="main-compare-btn"
              disabled={selectedProducts.length === 0}
              onClick={handleCompare}
            >
              Сравнить
            </button>
            {error && <p className="error-text">{error}</p>}
          </div>
        </div>
      </div>

      <div className="cards-bg">
        {compareData && compareData.length > 0 && (
          <div className="compare-results">
            <div className="compare-cards-flex">
              {compareData.map((item, index) => (
                <ShortCompareCard
                  key={index}
                  data={item}
                  bg={`short-product${index + 1}`}
                />
              ))}
            </div>

            {compareData.length >= 2 && (
              <button
                className="more-btn"
                onClick={() =>
                  navigate("/compare", {
                    state: {
                      products: compareData,
                    },
                  })
                }
              >
                Подробнее
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
