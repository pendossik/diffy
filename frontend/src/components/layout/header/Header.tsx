import { useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom"; // navigate нужен для кликов по кнопкам
import { useTranslation } from "react-i18next";
import { useClickOutside } from "../../../hooks/useClickOutside"; // <--- Импорт
import { useCurrentUser } from "../../../hooks/useCurrentUser"; // <--- Импорт

import Logo from "../../../assets/icons/Diffy.svg"; // Пути могут отличаться, проверь свои
import Favorites from "../../../assets/icons/Favourite.svg";
import User from "../../../assets/icons/User.svg";
import "./Header.css";

export default function Header() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();

    // 1. Используем хук для юзера (логика ушла отсюда)
    const { user, logout } = useCurrentUser();

    // 2. Логика для дропдауна
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // 3. Используем хук клика снаружи (логика ушла отсюда)
    useClickOutside(dropdownRef, () => setIsDropdownOpen(false));

    const toggleLanguage = () => {
        const newLang = i18n.language === "ru" ? "en" : "ru";
        i18n.changeLanguage(newLang);
    };

    const handleUserClick = (e: React.MouseEvent) => {
        if (!user) {
            navigate("/login");
        } else {
            e.preventDefault();
            setIsDropdownOpen(!isDropdownOpen);
        }
    };

    // Logout теперь просто вызывает функцию из хука, но нужно закрыть меню
    const onLogoutClick = () => {
        setIsDropdownOpen(false);
        logout();
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
                            {t("nav.gadgets")}
                        </a>
                    </li>
                    <li>
                        <a href="#parts" className="header-link">
                            {t("nav.parts")}
                        </a>
                    </li>
                </ul>

                <div className="header-actions">
                    <button
                        onClick={toggleLanguage}
                        className="header-lang-button"
                    >
                        {i18n.language === "ru" ? "RU" : "EN"}
                    </button>

                    <Link
                        to={user ? "/favorites" : "/login"}
                        className="action-link"
                        title="Избранное"
                    >
                        <img src={Favorites} alt="Избранное" />
                    </Link>

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

                        {user && isDropdownOpen && (
                            <div className="account-dropdown">
                                <div className="dropdown-email">
                                    {user.email}
                                </div>

                                <Link to="/profile" className="dropdown-item">
                                    <img
                                        src={User}
                                        alt=""
                                        className="dropdown-icon"
                                    />
                                    {t("user.manageAccount")}
                                </Link>

                                <button
                                    onClick={onLogoutClick}
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
                                            <line
                                                x1="21"
                                                y1="12"
                                                x2="9"
                                                y2="12"
                                            />
                                        </svg>
                                    </span>
                                    {t("user.logout")}
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </nav>
        </header>
    );
}
