import { useEffect, useState, useRef } from "react";
import axios from "axios";

type Props = {
  text: string;
  value: string;
  onChange: (id: number, name: string) => void;
};

type Product = {
  id: number;
  name: string;
};

export default function Search({ text, value, onChange }: Props) {
  const [products, setProducts] = useState<Product[]>([]);
  const [filtered, setFiltered] = useState<Product[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const wrapperRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_URL}/api/compare/products/`)
      .then((response) => setProducts(response.data))
      .catch((error) => console.error("Ошибка загрузки:", error));
  }, []);

  // Закрытие подсказок при клике вне компонента
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(event.target as Node)
      ) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const text = e.target.value;
    onChange(0, text); // обновляем текст
    const filteredProducts = products.filter((p) =>
      p.name.toLowerCase().includes(text.toLowerCase()),
    );
    setFiltered(filteredProducts);
    setIsOpen(true);
  }

  function handleSelect(product: Product) {
    onChange(product.id, product.name);
    setIsOpen(false);
  }

  return (
    <div className="search-wrapper" ref={wrapperRef}>
      <input
        placeholder={text}
        value={value}
        onChange={handleInputChange}
        onFocus={() => setIsOpen(true)}
        className="search-input"
      />
      {isOpen && filtered.length > 0 && (
        <ul className="search-dropdown">
          {filtered.map((p) => (
            <li key={p.id} onClick={() => handleSelect(p)}>
              {p.name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
