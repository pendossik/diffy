import { useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { useClickOutside } from "../../../hooks/useClickOutside"; 
import { useCurrentUser } from "../../../hooks/useCurrentUser";

import Logo from "../../../assets/icons/Diffy.svg";
import Favorites from "../../../assets/icons/Favourite.svg";
import User from "../../../assets/icons/User.svg";
import "./Header.css";

export default function Header() {
    const { t, i18n } = useTranslation();
    const navigate = useNavigate();

    // Логика пользователя и дропдауна
    const { user, logout } = useCurrentUser();
    const [isDropdownOpen, setIsDropdownOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    // Закрытие при клике вне
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

    const onLogoutClick = () => {
        logout();
        setIsDropdownOpen(false);
        navigate("/");
    };

    return (
        <header className="main-header">
            <nav className="header-nav">
                <Link to="/" className="logo-link">
                    <img src={Logo} alt="Diffy" />
                </Link>

                <ul className="nav-menu">
                    <li>
                        <a href="#gadgets" className="header-link">{t("nav.gadgets")}</a>
                    </li>
                    <li>
                        <a href="#parts" className="header-link">{t("nav.parts")}</a>
                    </li>
                </ul>

                <div className="header-actions">
                    <button onClick={toggleLanguage} className="header-lang-button">
                        {i18n.language.toUpperCase()}
                    </button>

                    <Link 
                        to={user ? "/favorites" : "/login"} 
                        className="action-link"
                        title={t("nav.favorites")}
                    >
                        <img src={Favorites} alt="Favorites" />
                    </Link>

                    <div className="user-profile-container" ref={dropdownRef}>
                        <button onClick={handleUserClick} className="action-link profile-btn">
                            <img src={User} alt="Profile" />
                        </button>

                        {user && isDropdownOpen && (
                            <div className="account-dropdown">
                                <div className="dropdown-email">{user.email}</div>

                                <Link 
                                    to="/profile" 
                                    className="dropdown-item" 
                                    onClick={() => setIsDropdownOpen(false)}
                                >
                                    <img src={User} alt="" className="dropdown-icon" />
                                    {t("user.manageAccount")}
                                </Link>

                                <button onClick={onLogoutClick} className="dropdown-item logout-btn">
                                    <span className="logout-icon">
                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                                            <polyline points="16 17 21 12 16 7" />
                                            <line x1="21" y1="12" x2="9" y2="12" />
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