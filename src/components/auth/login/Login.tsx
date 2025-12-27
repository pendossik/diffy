import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./login.css";
import axios from "axios";

export function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      const response = await axios.post(
        `${import.meta.env.VITE_API_URL}/api/token/`,
        {
          email: email, // если ты используешь email как логин
          password: password,
        },
      );

      const { access, refresh } = response.data;

      // сохраняем токены
      localStorage.setItem("access_token", access);
      localStorage.setItem("refresh_token", refresh);

      alert("Вы вошли в аккаунт!");
      navigate("/");
      window.location.reload();
    } catch (error: any) {
      console.error("Ошибка входа:", error.response?.data || error.message);
      alert("Неверный логин или пароль");
    }
  };

  return (
    <main className="auth">
      <div className="auth__inner">
        <div className="auth__image">
          <img
            src="./src/images/iPhone-17.png"
            alt="Photo_Iphone_17_Pro_dark-blue"
          />
        </div>
        <div className="auth__form">
          <h1>Войти в Diffy</h1>
          <p>Введите данные ниже</p>
          <form onSubmit={handleSubmit} action="">
            <input
              type="email"
              placeholder="Эл.почта"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            <input
              type="password"
              placeholder="Пароль"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            <button type="submit">Войти</button>
            <Link to="/">Забыли пароль?</Link>
          </form>
          <div className="auth__footer">
            <span>Нет аккаунта?</span>
            <Link to="/register" className="auth__link">
              Зарегистрироваться
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}
