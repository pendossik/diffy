import { BASE_URL } from "../utils/constants";
import { type Product } from "../types/product";

export const fetchProducts = async (
  searchQuery: string = "",
  method: "GET" | "POST" = "GET",
): Promise<Product[]> => {
  const response = await fetch(`${BASE_URL}${searchQuery}`, {
    method,
  });

  if (!response.ok) {
    throw new Error(`Ошибка: ${response.status}`);
  }

  const data: Product[] = await response.json();
  console.log("API RESPONSE:", data);

  return data.map((product) => ({
    id: product.id,
    name: product.name,
  }));
};
