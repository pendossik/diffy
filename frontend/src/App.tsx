import { BrowserRouter } from "react-router-dom";
import { AppRoutes } from "./routes/AppRoutes";
import Header from "./components/layout/header/Header";
import Footer from "./components/layout/footer/Footer";

function App() {
    return (
        <BrowserRouter>
            <Header />
            <main>
                <AppRoutes />
            </main>
            <Footer />
        </BrowserRouter>
    );
}

export default App;
