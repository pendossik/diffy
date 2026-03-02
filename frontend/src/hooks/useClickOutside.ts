/** * Хук для закрытия элементов (меню, дропдаунов) при клике вне их области
 */
import { useEffect, type RefObject } from "react";

export const useClickOutside = <T extends HTMLElement>(
    ref: RefObject<T | null>, // Добавили | null, так как useRef(null) в Header именно такой
    handler: () => void,
) => {
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            // Проверяем, что реф существует и клик был НЕ по нему
            if (ref.current && !ref.current.contains(event.target as Node)) {
                handler();
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () => {
            document.removeEventListener("mousedown", handleClickOutside);
        };
    }, [ref, handler]);
};
