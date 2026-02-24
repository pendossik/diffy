import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./register.css";
import axios from "axios";
import { useTranslation } from "react-i18next";

export function Register() {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/accounts/register/`,
        {
          username: name,
          email: email,
          password: password,
        },
      );

      console.log("Пользователь создан:", response.data);
      alert(t("auth.registerSuccess"));
      navigate("/login");
    } catch (error: any) {
      console.error(
        "Ошибка при регистрации:",
        error.response?.data || error.message,
      );
      alert(
        t("auth.registerError") +
          (error.response?.data?.detail || t("auth.checkData")),
      );
    }
  }

  return (
    <main className="reg">
      <div className="reg__inner">
        <div className="reg__image">
          <img
            src="./src/images/iPhone-17.png"
            alt="Photo_Iphone_17_Pro_dark"
          />
        </div>
        <div className="reg__form">
          <h1>{t("auth.registerTitle")}</h1>
          <p>{t("auth.registerSubtitle")}</p>

          <form onSubmit={handleSubmit}>
            <div className="form__group">
              <label htmlFor="name">{t("auth.nameLabel")}</label>
              <input
                id="name"
                type="text"
                placeholder=""
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </div>

            <div className="form__group">
              <label htmlFor="email">{t("auth.emailLabel")}</label>
              <input
                id="email"
                type="email"
                placeholder=""
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>

            <div className="form__group">
              <label htmlFor="password">{t("auth.passwordLabel")}</label>
              <input
                id="password"
                type="password"
                placeholder=""
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            <button type="submit" className="btn-create__acc">
              {t("auth.createAccountButton")}
            </button>

            <button type="button" className="btn-google">
              <img
                src="./src/icons/Google.svg"
                alt="Google"
                className="google-icon"
              />
              {t("auth.googleButton")}
            </button>
          </form>

          <div className="reg__footer">
            <span>{t("auth.alreadyHaveAccount")}</span>

            <Link to="/login" className="reg__link">
              {t("auth.loginLink")}
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
