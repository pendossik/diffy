import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import Iphone from '../assets/iPhone-17.png'

export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const navigate = useNavigate();

     const handleSubmit = (e) => {

        const users = JSON.parse(localStorage.getItem('users') || '[]');

        const user = users.find(
            (u) => u.email === email && u.password === password
        );

        if (user) {
            alert('Всё гуд! Вы вошли в аккаунт.');
            navigate('/');
        } else {
            alert('Нет такого пользователя или неверный пароль.');
        }
    };
    return(
        <main className="auth">
        <div className="auth__inner">
            <div className="auth__image">
                <img src={Iphone} alt="Photo_Iphone_17_Pro_dark-blue"/>
            </div>
            <div className="auth__form">
                <h1>Войти в Diffy</h1>
                <p>Введите данные ниже</p>
                <form onSubmit={handleSubmit} action="">
                    <input type="email" placeholder="Эл.почта" value={email} onChange={(e) => setEmail(e.target.value)} required/>
                    <input type="password" placeholder="Пароль" value={password} onChange={(e) => setPassword(e.target.value)} required/>
                    <button type="submit">Войти</button>
                    <Link to="/">Забыли пароль?</Link>
                </form>
                <div className="auth__footer">
                    <span>Нет аккаунта?</span>
                    <Link to="/register" className="auth__link">Зарегистрироваться</Link>
                </div>
             </div>
        </div>
    </main>
    )
}