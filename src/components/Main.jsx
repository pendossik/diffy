import { useState } from "react";
import Button from "./Button";
import Search from "./Search";
import Plus from "../assets/Plus.svg";
import CompareCard from "./CompareCard";

export default function Main() {
  const [firstProduct, setFirstProduct] = useState("");
  const [secondProduct, setSecondProduct] = useState("");
  const [showComparison, setShowComparison] = useState(false);

  const handleCompare = () => {
    setShowComparison(true);
  };

  return (
    <main>
      <div className="search-blocks">
        <div className="search">
          <Search
            text="Введите первый товар "
            value={firstProduct}
            onChange={(e) => setFirstProduct(e.target.value)}
          />
          <img src={Plus} alt="plus" />
          <Search
            text="Введите второй товар"
            value={secondProduct}
            onChange={(e) => setSecondProduct(e.target.value)}
          />
        </div>
        <div className="compare-button">
          <Button text={"Сравнить"} onClick={handleCompare} />
        </div>
      </div>
      <div className="a">
        {showComparison && (
          <div className="compare">
            <CompareCard product={firstProduct} />
            <CompareCard product={secondProduct} />
          </div>
        )}
      </div>
    </main>
  );
}
