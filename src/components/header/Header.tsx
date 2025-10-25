import "./header.css";
import { Link } from 'react-router-dom';

export default function Header() {
    return (
        <header className="header">
            <div className="header__inner">
                <Link to="/" className="header__logo logo">
                    <img src="./src/icons/Diffy.svg" alt="Diffy_logo" className="header__image" />
                </Link>
                <nav className="header__menu">
                    <ul className="header__menu-list">
                        <li className="header__menu-item">
                            Гаджеты
                            <Link to="/" className="header__menu-link"></Link>
                        </li>
                        <li className="header__menu-item">
                            Комплектующие ПК
                            <Link to="/" className="header__menu-link"></Link>
                        </li>
                        <li className="header__menu-item">
                            <Link to="/login" className="header__menu-link">Авторизация</Link>
                        </li>
                    </ul>
                </nav>
                <div className="header__menu-button">
                    <Link to ="/" className="header__button-like">
                        <img src="./src/icons/Favourite.svg" alt="header__button-like-image" />
                    </Link>
                    {/* нужно будет переименовать класс у Link */}
                    <Link to="/register" className="header__button-account">
                        <img src="./src/icons/User.svg" alt="header__button-account-image" />  
                    </Link>
                </div>
            </div>
        </header>
    )
}