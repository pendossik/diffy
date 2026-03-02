import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import HttpBackend from "i18next-http-backend";
import LanguageDetector from "i18next-browser-languagedetector";

i18n
    // подгружает переводы из папки /public/locales
    .use(HttpBackend)
    // определяет язык пользователя (браузер, localStorage)
    .use(LanguageDetector)
    // прокидывает i18n в react
    .use(initReactI18next)
    // инициализация
    .init({
        fallbackLng: "ru", // язык по умолчанию
        debug: true, // пишем логи в консоль

        interpolation: {
            escapeValue: false, // React сам экранирует XSS
        },

        backend: {
            // путь, откуда i18next будет брать переводы
            loadPath: "/locales/{{lng}}/{{ns}}.json",
        },
    });

export default i18n;
