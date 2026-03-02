import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useTranslation } from "react-i18next";
import axios from "axios";

import Iphone from "../../../public/images/iPhone-17-Pro-Max.png";
import "./Login.css";

export function Login() {
    const { t } = useTranslation();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const navigate = useNavigate();

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        try {
            const response = await axios.post(
                `${import.meta.env.VITE_API_URL}/token/`,
                {
                    email: email,
                    password: password,
                },
            );

            const { access, refresh } = response.data;

            localStorage.setItem("access_token", access);
            localStorage.setItem("refresh_token", refresh);

            alert(t("auth.loginSuccess"));
            navigate("/");
            window.location.reload();
        } catch (error: any) {
            console.error(
                "Ошибка входа:",
                error.response?.data || error.message,
            );
            alert(t("auth.loginError"));
        }
    };

    return (
        <main className="auth">
            <div className="auth__inner">
                <div className="auth__image">
                    <img src={Iphone} alt="Photo_Iphone_17_Pro_dark-blue" />
                </div>
                <div className="auth__form">
                    <h1>{t("auth.loginTitle")}</h1>
                    <p>{t("auth.loginSubtitle")}</p>

                    <form onSubmit={handleSubmit} action="">
                        <input
                            type="email"
                            placeholder={t("auth.emailPlaceholder")}
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            required
                        />

                        <input
                            type="password"
                            placeholder={t("auth.passwordPlaceholder")}
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            required
                        />

                        <button type="submit">{t("auth.loginButton")}</button>

                        <Link to="/">{t("auth.forgotPassword")}</Link>
                    </form>

                    <div className="auth__footer">
                        <span>{t("auth.noAccount")}</span>

                        <Link to="/register" className="auth__link">
                            {t("auth.registerLink")}
                        </Link>
                    </div>
                </div>
            </div>
        </main>
    );
}
