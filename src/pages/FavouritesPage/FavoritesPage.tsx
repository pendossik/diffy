import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import "./FavouritesPage.css";
import { useTranslation } from "react-i18next";

interface Product {
  id: number;
  name: string;
  img: string;
}

interface FavoriteEntry {
  id: number;
  products: Product[];
  created_at: string;
}

export function FavoritesPage() {
  const [favorites, setFavorites] = useState<FavoriteEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [syncingId, setSyncingId] = useState<number | null>(null);

  const navigate = useNavigate();
  const token = localStorage.getItem("access_token");
  const { t } = useTranslation();

  useEffect(() => {
    if (!token) {
      navigate("/login");
      return;
    }

    axios
      .get(`${import.meta.env.VITE_API_URL}/compare/favorites/`, {
        headers: { Authorization: `Bearer ${token}` },
      })
      .then((res) => setFavorites(res.data))
      .catch((err) =>
        console.error("Ошибка при получении списка избранного:", err),
      )
      .finally(() => setLoading(false));
  }, [token, navigate]);

  const handleGoToCompare = async (group: FavoriteEntry) => {
    setSyncingId(group.id);

    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_URL}/compare/comparetest/`,
        {
          product_ids: group.products.map((p) => p.id),
        },
      );

      navigate("/compare", { state: { products: res.data } });
    } catch (err) {
      console.error("Ошибка при сборке данных для сравнения:", err);
      alert("Не удалось загрузить подробные данные товаров");
    } finally {
      setSyncingId(null);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(
        `${import.meta.env.VITE_API_URL}/compare/favorites/${id}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        },
      );
      setFavorites((prev) => prev.filter((f) => f.id !== id));
    } catch (err) {
      alert("Ошибка при удалении");
    }
  };

  if (loading) {
    return (
      <div className="fav-page-wrapper">
        <h2 style={{ color: "white", textAlign: "center", marginTop: "100px" }}>
          {t("favourites.favLoading")}
        </h2>
      </div>
    );
  }

  return (
    <main className="fav-page-wrapper">
      <h1 className="fav-title">{t("favourites.favCompares")}</h1>
      <div className="favorites-list">
        {favorites.length === 0 ? (
          <p
            className="no-data"
            style={{ color: "white", textAlign: "center" }}
          >
            {t("favourites.noneFavouriteCompares")}
          </p>
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
                        <img src={p.img} alt={p.name} />
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
                  style={{
                    marginTop: "20px",
                    height: "45px",
                    opacity: syncingId !== null && !isThisLoading ? 0.5 : 1,
                    cursor: syncingId !== null ? "not-allowed" : "pointer",
                  }}
                  disabled={syncingId !== null}
                  onClick={() => handleGoToCompare(group)}
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
