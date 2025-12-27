import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./components/body/HomePage";
import Header from "./components/header/Header";
import Footer from "./components/footer/Footer";
import { Login } from "./components/auth/login/Login";
import { Register } from "./components/auth/register/Register";
import { ComparePage } from "./components/body/ComparePage";
import { FavoritesPage } from "./components/body/FavoritesPage";

function App() {
  return (
    <BrowserRouter>
      <Header />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/compare" element={<ComparePage />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/favorites" element={<FavoritesPage />} />
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  );
}

export default App;
