import './header.css';
import Logo from '../../icons/Diffy.svg';
import Favorites from '../../icons/Favourite.svg';
import User from '../../icons/User.svg';

export default function Header() {
  return(
  <header>
    <nav>
      <a className="header-link" href="/"><img src={Logo} alt='Diffy' /></a>
      <a className="header-link" href="#gadgets">Гаджеты</a>
      <a className="header-link" href="#parts">Комплектующие</a>
      <a className="header-link" href="/register">Регистрация</a>
      <div className="header-section">
        <a href='#favorites'><img src={Favorites} alt='Favorites' /></a>
        <a href='/login'><img src={User} alt='User' /></a>
      </div>
    </nav>
  </header>
  );
}
