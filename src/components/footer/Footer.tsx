import "./footer.css";

export default function Footer() {
  return (
    <footer>
      <div className="footer-container">
        <div className="footer-logo-section">
          <a href="/" className="footer-logo">
            <img src="./src/icons/White_Diffy.svg" alt="Logo" />
          </a>
        </div>

        <div>
          <ul>
            <li>
              <h3 className="footer-header">Поддержка</h3>
            </li>
            <li>
              <a href="mailto:diffy@gmail.com" className="footer-text">
                diffy@gmail.com
              </a>
            </li>
            <li>
              <p className="footer-text">+7-123-456-78-90</p>
            </li>
          </ul>
        </div>

        <div>
          <ul>
            <li>
              <h3 className="footer-header">Аккаунт</h3>
            </li>
            <li>
              <a href="/" className="footer-text">
                Мой аккаунт
              </a>
            </li>
            <li>
              <a href="/register" className="footer-text">
                Вход/Регистрация
              </a>
            </li>
          </ul>
        </div>

        <div>
          <ul>
            <li>
              <h3 className="footer-header">О нас</h3>
            </li>
            <li>
              <a href="/" className="footer-text">
                Политика конфиденциальности
              </a>
            </li>
            <li>
              <a href="/" className="footer-text">
                FAQ
              </a>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
