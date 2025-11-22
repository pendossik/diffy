import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "./register.css"
import axios from "axios";


export function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    async function handleSubmit(e: React.FormEvent) {
        e.preventDefault();

        try {
            const response = await axios.post("http://127.0.0.1:8000/accounts/api/register/", {
                username: name,
                email: email,
                password: password,
            });

            console.log("Пользователь создан:", response.data);
            alert("Аккаунт создан успешно!");
            navigate("/login");
        } catch (error: any) {
            console.error("Ошибка при регистрации:", error.response?.data || error.message);
            alert("Ошибка регистрации: " + (error.response?.data?.detail || "проверь данные"));
        }
    }


    return (
<<<<<<< HEAD
        <main className="reg">
            <div className="reg__inner">
            <div className="reg__image">
                <img src="./src/images/iPhone-17.png" alt="Photo_Iphone_17_Pro_dark" />
            </div>
                <div className="reg__form">
                    <h1>Создать аккаунт</h1>
                    <p>Введите данные ниже</p>
                    <form onSubmit={handleSubmit}>
                        <div className="form__group">
                            <label htmlFor="name">Имя</label>
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
                            <label htmlFor="email">Эл. почта</label>
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
                            <label htmlFor="password">Пароль</label>
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
                            Создать аккаунт
                        </button>
                        <button type="button" className="btn-google">
                            <img
                            src="./src/icons/Google.svg"
                            alt="Google"
                            className="google-icon"
                            />
                            Войти через Google
                        </button>
                    </form>
                    <div className="reg__footer">
                        <span>Уже есть аккаунт?</span>
                        <Link to="/login" className="reg__link">
                            Войти
                        </Link>
                    </div>
                </div>
=======
        <main className="auth">
            <div className="auth__inner">
            <div className="auth__image">
                <img src="./src/images/iPhone-17.png" alt="Photo_Iphone_17_Pro_dark" />
            </div>
            <div className="auth__form">
                <h1>Создать аккаунт</h1>
                <p>Введите данные ниже</p>
                <form onSubmit={handleSubmit}>
                <div className="form__group">
                    <label htmlFor="name">Имя</label>
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
                    <label htmlFor="email">Эл. почта</label>
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
                    <label htmlFor="password">Пароль</label>
                    <input
                    id="password"
                    type="password"
                    placeholder=""
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    />
                </div>
                <button type="submit" className="btn-primary">
                    Создать аккаунт
                </button>
                <button type="button" className="btn-google">
                    <img
                    src="./src/icons/Google.svg"
                    alt="Google"
                    className="google-icon"
                    />
                    Войти через Google
                </button>
                </form>
                <div className="auth__footer">
                <span>Уже есть аккаунт?</span>
                <Link to="/login" className="auth__link">
                    Войти
                </Link>
                </div>
            </div>
>>>>>>> karen
            </div>
        </main>
        );
}