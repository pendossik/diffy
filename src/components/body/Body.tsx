import "./body.css";
import Search from "./Search";
import { useState } from "react";
import CompareCard from "./CompareCard";
import { useNavigate } from "react-router-dom";

export function Body() {
  const [firstProduct, setFirstProduct] = useState("");
  const [secondProduct, setSecondProduct] = useState("");
  const [showComparison, setShowComparison] = useState(false);
  const navigate = useNavigate();

  return (
    <main>
      <div className="search-block">
        <div className="search-compare">
          <Search
            text="Название первого товара"
            value={firstProduct}
            onChange={(e) => setFirstProduct(e.target.value)}
          />

          <img src="./src/icons/Plus.svg" alt="image plus" width="70" />

          <Search
            text="Название второго товара"
            value={secondProduct}
            onChange={(e) => setSecondProduct(e.target.value)}
          />
        </div>
        <div className="compare-button">
          <button onClick={() => setShowComparison(true)}>Сравнить</button>
        </div>
      </div>
      <div className="cards-bg">
        {showComparison && (
          <div>
            <div className="compare">
              <CompareCard productName={firstProduct} bg="short-product1" />
              <CompareCard productName={secondProduct} bg="short-product2" />
            </div>

            <button className="more-btn"
              onClick={() => {
                navigate("/compare", {
                  state: { firstProduct, secondProduct },
                });
              }}
            >
              Подробнее
            </button>
          </div>
        )}
      </div>
    </main>
  );
}
