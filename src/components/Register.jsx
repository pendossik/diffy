import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import "../register.css"
import Iphone from '../assets/iPhone-17.png'

export default function Register() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('')
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

    function handleSubmit() {
    

        const users = JSON.parse(localStorage.getItem('users') || '[]'); // Берем пользователей

        const exists = users.some((user) => user.email === email); // true or false; провертка на emaill
        if(exists){
            alert('Пользователь с таким email существует')
            return;
        }

        users.push({name, email, password});
        localStorage.setItem('users', JSON.stringify(users));

        alert('Аккаунт создан');
        navigate('/login');
    }

    return (
        <main className="auth">
            <div className="auth__inner">
            <div className="auth__image">
                <img src={Iphone} alt="Photo_Iphone_17_Pro_dark" />
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
                    src=""
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
            </div>
        </main>
        );
}