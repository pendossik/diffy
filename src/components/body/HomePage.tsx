import "./body.css";
import Search from "./Search";
import { useState } from "react";
import ShortCompareCard from "./ShortCompareCard";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { useTranslation } from "react-i18next";

import favOff from "../../icons/Favourite_button.svg";
import favOn from "../../icons/Favourite_button_active.svg";

type Product = {
  id: number;
  name: string;
};

export function HomePage() {
  const { t } = useTranslation();
  const [products, setProducts] = useState<Product[]>([
    { id: 0, name: "" }, // первый
    { id: 0, name: "" }, // второй
    { id: 0, name: "" }, // третий
  ]);

  const [compareData, setCompareData] = useState<any[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isFav, setIsFav] = useState(false);
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
      setError(t("home.errorSelect"));
      return;
    }
    if (hasDuplicates) {
      setError(t("home.errorUnique"));
      return;
    }

    axios
      .post(`${import.meta.env.VITE_API_URL}/api/compare/comparetest/`, {
        product_ids: selectedProducts.map((p) => p.id),
      })
      .then((res) => {
        console.log("RESPONSE:", res.data);
        setCompareData(res.data);
        setIsFav(false); // Сбрасываем лайк при новом поиске
      })
      .catch(() => setError(t("home.errorLoad")));
  };

  const handleSaveToFavorites = async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      alert("t('home.alertLogin')");
      return;
    }

    try {
      // Отправляем ID всех найденных товаров (compareData)
      await axios.post(
        `${import.meta.env.VITE_API_URL}/api/compare/favorites/`,
        { product_ids: compareData?.map((p: any) => p.id) },
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      setIsFav(true);
      alert("t('home.alertSaved')");
    } catch (err) {
      console.error(err);
      alert(t("home.alertSaveError"));
    }
  };

  return (
    <main>
      <div className="search-section">
        <div className="search-container">
          <div className="search-inputs">
            <Search
              text={t("home.searchPlaceholder1")}
              value={products[0].name}
              onChange={(id, name) => updateProduct(0, id, name)}
            />

            {products[0].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src="./src/icons/Plus.svg" alt="plus" width="70" />
                </div>
                <Search
                  text={t("home.searchPlaceholder2")}
                  value={products[1].name}
                  onChange={(id, name) => updateProduct(1, id, name)}
                />
              </>
            )}

            {products[1].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src="./src/icons/Plus.svg" alt="plus" width="70" />
                </div>
                <Search
                  text={t("home.searchPlaceholder3")}
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
              {t("home.compareBtn")}
            </button>
            {error && <p className="error-text">{error}</p>}
          </div>
        </div>
      </div>

      <div className="cards-bg">
        {compareData && compareData.length > 0 && (
          <div
            className="compare-results"
            style={{ position: "relative", paddingBottom: "50px" }}
          >
            {/* Кнопка-сердце */}
            <button
              className="fav-btn-main"
              onClick={handleSaveToFavorites}
              style={{
                all: "unset",
                position: "absolute",
                top: "20px",
                right: "40px",
                cursor: "pointer",
                zIndex: 10,
              }}
            >
              <img
                src={isFav ? favOn : favOff}
                alt="heart"
                style={{ width: "45px" }}
              />
            </button>

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
                style={{ marginTop: "40px" }}
                onClick={() =>
                  navigate("/compare", {
                    state: { products: compareData },
                  })
                }
              >
                {t("home.moreBtn")}
              </button>
            )}
          </div>
        )}
      </div>
    </main>
  );
}
