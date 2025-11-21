// import Records from '../../records.json';
import { useEffect, useState } from "react";
import axios from "axios";
 
type Props = {
  text: string;
  value: string;
  // было (e: React.ChangeEvent<HTMLInputElement>) 
  onChange: (id: number, name: string) => void;
}
 
type Product = {
  id: number;
  name: string;
};
 
 
export default function Search({ text, value, onChange }: Props) {
  // При выборе товара будем хранить не только его имя, но и id,
  // чтобы CompareCard знал, какой именно товар запрашивать.
  const [products, setProducts] = useState<Product[]>([]);
 
  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/compare/products/")
      .then((response) => setProducts(response.data))
      .catch((error) => console.error("Ошибка загрузки:", error));
  }, []);
 
  function handleSelect(e: React.ChangeEvent<HTMLInputElement>) {
    const name = e.target.value;
    const product = products.find((p) => p.name === name);
    onChange(product ? product.id : 0, name);
  }
 
  return (
    <div className="search-input-wrapper">
      <input
        placeholder={text}
        value={value}
        onChange={handleSelect}
        list="items"
        className="search-input"
      />
      <datalist id="items">
        {products.map((product) => (
          <option key={product.id} value={product.name} />
        ))}
      </datalist>
    </div>
  );
}