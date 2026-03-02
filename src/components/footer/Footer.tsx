import "./Footer.css";
import { useTranslation } from "react-i18next";

export default function Footer() {
  const { t } = useTranslation();

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
              <h3 className="footer-header">{t("footer.support")}</h3>
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
              <h3 className="footer-header">{t("footer.account")}</h3>
            </li>
            <li>
              <a href="/" className="footer-text">
                {t("footer.myAccount")}
              </a>
            </li>
            <li>
              <a href="/register" className="footer-text">
                {t("footer.signInUp")}
              </a>
            </li>
          </ul>
        </div>

        <div>
          <ul>
            <li>
              <h3 className="footer-header">{t("footer.aboutUs")}</h3>
            </li>
            <li>
              <a href="/" className="footer-text">
                {t("footer.privacyPolicy")}
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
