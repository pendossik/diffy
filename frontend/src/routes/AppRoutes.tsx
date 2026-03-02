import { Route, Routes } from "react-router-dom";
import { HomePage } from "../pages/HomePage/HomePage";
import { ComparePage } from "../pages/ComparePage/ComparePage";
import { Login } from "../features/Login/Login";
import { Register } from "../features/Register/Register";
import { FavoritesPage } from "../pages/FavouritesPage/FavoritesPage";

export const AppRoutes = () => {
    return (
        <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/favorites" element={<FavoritesPage />} />
        </Routes>
    );
};
