import { StrictMode, Suspense } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import axios from "axios";
import i18n from "./i18n";
import "./theme/index.css";

axios.interceptors.request.use((config) => {
    config.headers["Accept-Language"] = i18n.language;
    return config;
});

createRoot(document.getElementById("root")!).render(
    <StrictMode>
        <Suspense fallback="<div>Loading...</div>">
            <App />
        </Suspense>
    </StrictMode>,
);
