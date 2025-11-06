import "./footer.css"

export default function Footer() {
  return (
    <footer>
      <div className="footer">
        <a href="/" className="footer-logo">
          <img src="./src/icons/White_Diffy.svg" alt="White_Diffy_logo" />
        </a>
      </div>
      <div className="footer">
        <ul>
          <li>
            <h3 className="footer-header" >Поддержка</h3>
          </li>
          <li>
            <a href="/" className="footer-text">
              diffy@gmail.com
            </a>
          </li>
          <li>
            <p className="footer-text">+7-123-456-78-90</p>
          </li>
        </ul>
      </div>
      <div className="footer">
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
            <a href="/" className="footer-text">
              Вход/Регистрация
            </a>
          </li>
          <li>
            <a href="/" className="footer-text">
              Избранное
            </a>
          </li>
        </ul>
      </div>
      <div>
        <ul>
          <li>
            <h3 className="footer-header" >О нас</h3>
          </li>
          <li>
            <a href="/" className="footer-text">
              Политика конфиденциальности
            </a>
          </li>
          <li>
            <a href="/" className="footer-text">
              Правила соглашения
            </a>
          </li>
          <li>
            <a href="/" className="footer-text">
              FAQ
            </a>
          </li>
          <li>
            <a href="/" className="footer-text">
              Контакты
            </a>
          </li>
        </ul>
      </div>
    </footer>
  );
}
