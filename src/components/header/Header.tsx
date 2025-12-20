import { useState, useEffect, useRef } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import Logo from "../../icons/Diffy.svg";
import Favorites from "../../icons/Favourite.svg";
import User from "../../icons/User.svg";
import "./header.css";

interface UserData {
  email: string;
}

export default function Header() {
  const [user, setUser] = useState<UserData | null>(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null); // Реф для отслеживания клика вне меню
  const navigate = useNavigate();

  // 1. Получаем данные пользователя
  useEffect(() => {
    const fetchUser = async () => {
      const token = localStorage.getItem("access_token");
      if (!token) return;

      try {
        const response = await axios.get(
          `${import.meta.env.VITE_API_URL}/api/accounts/current_user/`,
          {
            headers: {
              // Если Bearer не сработает, попробуй заменить на: Authorization: `JWT ${token}`
              Authorization: `Bearer ${token}`,
            },
          },
        );
        // На фото 4 видно структуру: response.data содержит поле email
        setUser(response.data);
      } catch (error: any) {
        console.error("Детальная ошибка бэка:", error.response?.data);
        // Если токен плохой, убираем его, чтобы кнопка снова вела на /login
        if (error.response?.status === 401) {
          localStorage.removeItem("access_token");
          setUser(null);
        }
      }
    };
    fetchUser();
  }, []);

  // 2. Закрытие меню при клике в любое другое место экрана
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUser(null);
    setIsDropdownOpen(false);
    navigate("/");
  };

  const handleUserClick = (e: React.MouseEvent) => {
    if (!user) {
      navigate("/login");
    } else {
      e.preventDefault();
      setIsDropdownOpen(!isDropdownOpen);
    }
  };

  return (
    <header className="main-header">
      <nav className="header-nav">
        <Link to="/" className="logo-link">
          <img src={Logo} alt="Diffy - Главная" />
        </Link>

        <ul className="nav-menu">
          <li>
            <a href="#gadgets" className="header-link">
              Гаджеты
            </a>
          </li>
          <li>
            <a href="#parts" className="header-link">
              Комплектующие
            </a>
          </li>
          {!user && (
            <li>
              <Link to="/register" className="header-link">
                Регистрация
              </Link>
            </li>
          )}
        </ul>

        <div className="header-actions">
          <a href="#favorites" className="action-link" title="Избранное">
            <img src={Favorites} alt="Избранное" />
          </a>

          {/* Контейнер профиля с рефом */}
          <div className="user-profile-container" ref={dropdownRef}>
            <button
              onClick={handleUserClick}
              className="action-link profile-btn"
              style={{
                background: "none",
                border: "none",
                padding: 0,
                cursor: "pointer",
              }}
            >
              <img src={User} alt="Профиль" />
            </button>

            {/* Выпадающее меню */}
            {user && isDropdownOpen && (
              <div className="account-dropdown">
                <div className="dropdown-email">{user.email}</div>

                <Link to="/profile" className="dropdown-item">
                  <img src={User} alt="" className="dropdown-icon" />
                  Manage My Account
                </Link>

                <button
                  onClick={handleLogout}
                  className="dropdown-item logout-btn"
                >
                  <span className="logout-icon">
                    <svg
                      width="16"
                      height="16"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                      <polyline points="16 17 21 12 16 7" />
                      <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                  </span>
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </nav>
    </header>
  );
}
