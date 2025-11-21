import { useEffect, useState } from "react";
import axios from "axios";
 
type Props = {
  productId: number;
};
 
type Characteristic = {
  id: number;
  name: string;
  value: string;
};
 
type Category = {
  id: number;
  name: string;
};
 
type Product = {
  id: number;
  name: string;
  category: Category;
  characteristics: Characteristic[];
};
 
export default function CompareCard({ productId }: Props) {
  const [productData, setProductData] = useState<Product | null>(null);
 
  useEffect(() => {
    if (!productId) return;
 
    axios
      .get(`http://127.0.0.1:8000/compare/products/${productId}/`)
      .then((response) => setProductData(response.data))
      .catch((error) => console.error("Ошибка загрузки:", error));
  }, [productId]);
 
  return (
    productData && (
      <div className="card">
        <h2>{productData.name}</h2>
        <p>Категория: {productData.category.name}</p>
        <hr />
        <h3>Характеристики</h3>
        <ul>
          {productData.characteristics.map((char) => (
            <li key={char.id}>
              {char.name}: {char.value}
            </li>
          ))}
        </ul>
      </div>
    )
  );
}