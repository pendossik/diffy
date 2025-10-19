import "./header.css";

export default function Header() {
    return (
        <header className="header">
            <div className="header__inner">
                <a href="/" className="header__logo logo">
                    <img src="./src/icons/Diffy.svg" alt="Diffy_logo" className="header__image" />
                </a>
                <nav className="header__menu">
                    <ul className="header__menu-list">
                        <li className="header__menu-item">
                            Гаджеты
                            <a href="/" className="header__menu-link"></a>
                        </li>
                        <li className="header__menu-item">
                            Комплектующие ПК
                            <a href="/" className="header__menu-link"></a>
                        </li>
                        <li className="header__menu-item">
                            Авторизация
                            <a href="/" className="header__menu-link"></a>
                        </li>
                    </ul>
                </nav>
                <button className="header__button-like"></button>
                <button className="header__button-account"></button>
            </div>
        </header>
    )
}