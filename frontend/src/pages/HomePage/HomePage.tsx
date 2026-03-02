import "./HomePage.css";
import Search from "../../features/Compare/Search/Search";
import { useState } from "react";
import ShortCompareCard from "../../features/Compare/ShortCompareCard/ShortCompareCard";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { type Product } from "../../types/product";
import { productService } from "../../api/services/product.service";

import favOff from "../../assets/icons/Favourite_button.svg";
import favOn from "../../assets/icons/Favourite_button_active.svg";
import Plus from "../../assets/icons/Plus.svg";

export function HomePage() {
  const { t } = useTranslation();
  const [products, setProducts] = useState<Product[]>([
    { id: 0, name: "" },
    { id: 0, name: "" },
    { id: 0, name: "" },
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

  const handleCompare = async () => {
    setError(null);
    const selectedIds = products.filter((p) => p.id !== 0).map((p) => p.id);

    if (selectedIds.length === 0) return setError(t("home.errorSelect"));

    try {
      const data = await productService.compare(selectedIds);
      setCompareData(data);
      setIsFav(false);
    } catch (err: any) {
      setError(t("home.errorLoad"));
    }
  };

  const handleSaveToFavorites = async () => {
    if (!compareData) return;

    try {
      const ids = compareData.map((p: any) => p.id);
      await productService.saveToFavorites(ids);
      setIsFav(true);
      alert(t("home.alertSaved"));
    } catch (err: any) {
      // Наш apiClient сам кинет ошибку, если нет токена (401)
      alert(t("home.alertSaveError"));
    }
  };

  return (
    <main>
      <div className="search-block">
        <div className="search-container">
          <div className="search-inputs">
            <Search
              placeholder={t("home.searchPlaceholder1")}
              value={products[0].name}
              onChange={(id, name) => updateProduct(0, id, name)}
            />

            {products[0].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src={Plus} alt="plus" width="70" />
                </div>
                <Search
                  placeholder={t("home.searchPlaceholder2")}
                  value={products[1].name}
                  onChange={(id, name) => updateProduct(1, id, name)}
                />
              </>
            )}

            {products[1].id !== 0 && (
              <>
                <div className="plus-icon">
                  <img src={Plus} alt="plus" width="70" />
                </div>
                <Search
                  placeholder={t("home.searchPlaceholder3")}
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