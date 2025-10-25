import "./footer.css"

export function Footer() {
    return (
        <footer className="footer">
            <div className="footer__inner">
                <div className="footer__logo-wrapper">
                    <a href="/" className="footer__logo logo">
                        <img src="./src/icons/White_Diffy.svg" alt="White_Diffy_logo" className="footer__image" />
                    </a>
                </div>
                <nav className="footer__menu">
                    <div className="footer__menu-column">
                        <h2>Поддержка</h2>
                        <ul className="footer__menu-list-supprot">
                            <li className="footer__menu-item">
                                diffy@gmail.com
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                +7-123-456-78-90
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                        </ul>
                    </div>
                    <div className="footer__menu-column">
                            <h2>Аккаунт</h2>
                        <ul className="footer__menu-list-supprot">
                            <li className="footer__menu-item">
                                Мой аккаунт
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                Вход/Регистрация
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                Избранное
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                        </ul>
                    </div>
                    <div className="footer__menu-column">
                            <h2>О нас</h2>
                        <ul className="footer__menu-list-supprot">
                            <li className="footer__menu-item">
                                Политика конфиденциальности
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                Правила соглашения
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                FAQ
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                            <li className="footer__menu-item">
                                Контакты
                                <a href="/" className="footer__menu-link"></a>
                            </li>
                        </ul>
                    </div>
                </nav>
            </div>
        </footer>
    )
}