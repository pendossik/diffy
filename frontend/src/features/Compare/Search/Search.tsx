import { useEffect, useState, useRef } from "react";
import { fetchProducts } from "../../../api/fetchProducts";
import { type Product } from "../../../types/product";
import "./Search.css";

type SearchProps = {
    placeholder: string;
    value: string;
    onChange: (id: number, name: string) => void;
};

export default function Search({ placeholder, value, onChange }: SearchProps) {
    const [results, setResults] = useState<Product[]>([]);
    const [isOpen, setIsOpen] = useState(false);
    const wrapperRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!value.trim()) {
            setResults([]);
            return;
        }

        const timeout = setTimeout(async () => {
            try {
                const data = await fetchProducts("/compare/products/");
                setResults(
                    data.filter((p) =>
                        p.name.toLowerCase().includes(value.toLowerCase()),
                    ),
                );
            } catch (e) {
                console.error(e);
            }
        }, 300);

        return () => clearTimeout(timeout);
    }, [value]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (
                wrapperRef.current &&
                !wrapperRef.current.contains(event.target as Node)
            ) {
                setIsOpen(false);
            }
        };

        document.addEventListener("mousedown", handleClickOutside);
        return () =>
            document.removeEventListener("mousedown", handleClickOutside);
    }, []);

    function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
        onChange(0, e.target.value);
        setIsOpen(true);
    }

    function handleSelect(product: Product) {
        onChange(product.id, product.name);
        setIsOpen(false);
    }

    return (
        <div className="search-wrapper" ref={wrapperRef}>
            <input
                placeholder={placeholder}
                value={value}
                onChange={handleInputChange}
                onFocus={() => setIsOpen(true)}
                className="search-input"
            />

            {isOpen && results.length > 0 && (
                <ul className="search-dropdown">
                    {results.map((p) => (
                        <li key={p.id} onClick={() => handleSelect(p)}>
                            {p.name}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
