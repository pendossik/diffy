import "./header.css";
import Logo from "../../icons/Diffy.svg";
import Favorites from "../../icons/Favourite.svg";
import User from "../../icons/User.svg";
import { Link } from "react-router-dom"; // Если используешь react-router

export default function Header() {
  return (
    <header className="main-header">
      <nav className="header-nav">
        {/* Логотип */}
        <a href="/" className="logo-link">
          <img src={Logo} alt="Diffy - Главная" />
        </a>

        {/* Основное меню */}
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
          <li>
            <a href="/register" className="header-link">
              Регистрация
            </a>
          </li>
        </ul>

        {/* Действия пользователя */}
        <div className="header-actions">
          <a href="#favorites" className="action-link" title="Избранное">
            <img src={Favorites} alt="Избранное" />
          </a>
          <a href="/login" className="action-link" title="Личный кабинет">
            <img src={User} alt="Профиль" />
          </a>
        </div>
      </nav>
    </header>
  );
}
