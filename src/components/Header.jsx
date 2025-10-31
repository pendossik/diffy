import '../index.css';
import Logo from '../assets/Logo.svg';
import Favorites from '../assets/Favorites.svg';
import User from '../assets/User.svg';

export default function Header() {
  return(
  <header>
    <nav>
      <a class='header-sections' href="/"><img src={Logo} alt='Diffy' /></a>
      <a class='header-sections' href="#gadgets">Гаджеты</a>
      <a class='header-sections' href="#parts">Комплектующие</a>
      <a class='header-sections' href="/register">Регистрация</a>
      <div class='header-sections'>
        <a href='#favorites'><img src={Favorites} alt='Favorites' /></a>
        <a href='/login'><img src={User} alt='User' /></a>
      </div>
    </nav>
  </header>
  );
}
