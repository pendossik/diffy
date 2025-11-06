import "./body.css";
import Search from "./Search";
import { useState } from "react";
import CompareCard from "./CompareCard";

export function Body() {
  const [firstProduct, setFirstProduct] = useState("");
  const [secondProduct, setSecondProduct] = useState("");
  const [showComparison, setShowComparison] = useState(false);

  return (
    <main>
      <div className="search-block">
        <div className="search-compare">
          <Search
            text="Название первого товара"
            value={firstProduct}
            onChange={(e) => setFirstProduct(e.target.value)}
          />

          <img src="./src/icons/Plus.svg" alt="image plus" />

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
      <img src="./src/images/Cat.png"></img>
      <div className="a">
        {showComparison && (
          <div className="compare">
            <CompareCard productName={firstProduct} />
            <CompareCard productName={secondProduct} />
          </div>
        )}
      </div>
    </main>
  );
}
