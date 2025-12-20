import { useEffect, useState } from "react";
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

  useEffect(() => {
    axios
      .get(`${import.meta.env.VITE_API_URL}/api/compare/products/`)
      .then((response) => setProducts(response.data))
      .catch((error) => console.error("Ошибка загрузки:", error));
  }, []);

  function handleSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const name = e.target.value;
    const product = products.find((p) => p.name === name);
    onChange(product ? product.id : 0, name);
  }

  return (
    <div>
      <input
        placeholder={text}
        value={value}
        onChange={handleSelect}
        list="items"
      />
      <datalist id="items">
        {products.map((product) => (
          <option key={product.id} value={product.name} />
        ))}
      </datalist>
    </div>
  );
}
