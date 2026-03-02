import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import {
  productService,
  type FavoriteEntry,
} from "../../api/services/product.service";
import "./FavouritesPage.css";

export function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<number | null>(null);

  const navigate = useNavigate();
  const { t } = useTranslation();

  // Загрузка данных
  useEffect(() => {
    const fetchFavs = async () => {
      try {
        const data = await productService.getFavorites();
        setFavorites(data);
      } catch (err) {
        console.error("Ошибка при получении избранного:", err);
      } finally {
        setLoading(false);
      }
    };

    fetchFavs();
  }, []);

  // Переход к сравнению
  const handleGoToCompare = async (group: FavoriteEntry) => {
    setSyncingId(group.id);
    try {
      const ids = group.products.map((p) => p.id);
      const detailedData = await productService.compare(ids);

      navigate("/compare", { state: { products: detailedData } });
    } catch (err) {
      alert(t("favourites.errorLoadDetails") || "Ошибка загрузки данных");
    } finally {
      setSyncingId(null);
    }
  };

  // Удаление контентуса из избранного
  const handleDelete = async (id: number) => {
    try {
      await productService.deleteFavorite(id);
      setFavorites((prev) => prev.filter((f) => f.id !== id));
    } catch (err) {
      alert(t("favourites.errorDelete") || "Ошибка при удалении");
    }
  };

  if (loading) {
    return (
      <div className="fav-page-wrapper">
        <h2 className="loading-text">{t("favourites.favLoading")}</h2>
      </div>
    );
  }

  return (
    <main className="fav-page-wrapper">
      <h1 className="fav-title">{t("favourites.favCompares")}</h1>
      <div className="favorites-list">
        {favorites.length === 0 ? (
          <p className="no-data">{t("favourites.noneFavouriteCompares")}</p>
        ) : (
          favorites.map((group) => {
            const isThisLoading = syncingId === group.id;
            return (
              <div key={group.id} className="fav-group-card">
                <button
                  className="delete-fav-icon"
                  onClick={() => handleDelete(group.id)}
                >
                  ×
                </button>

                <div className="fav-products-row">
                  {group.products.map((p, idx) => (
                    <div key={p.id} className="fav-item-mini">
                      <div className="fav-img-box">
                        <img src={p.img ?? ""} alt={p.name} />
                      </div>
                      <p>{p.name}</p>
                      {idx < group.products.length - 1 && (
                        <span className="vs-label">VS</span>
                      )}
                    </div>
                  ))}
                </div>

                <button
                  className="main-compare-btn"
                  disabled={syncingId !== null}
                  onClick={() => handleGoToCompare(group)}
                  style={{
                    opacity: syncingId !== null && !isThisLoading ? 0.5 : 1,
                  }}
                >
                  {isThisLoading
                    ? t("favourites.charLoading")
                    : t("favourites.details")}
                </button>
              </div>
            );
          })
        )}
      </div>
    </main>
  );
}