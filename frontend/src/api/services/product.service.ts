import { apiClient } from "../apiClient";
import { type Product } from "../../types/product";

export type FavoriteEntry = {
  id: number;
  products: Product[];
  created_at: string;
};

export type SearchData = {
  count: number,
  next: number | null,
  previous: number | null,
  results: Product[];
}

export const productService = {
  getAllProducts: () => apiClient.get<Product[]>("/catalog/products/"),

  searchProduct: (name: string) => apiClient.get<SearchData>(`/catalog/products/?search=${name}`),

  compare: (ids: number[]) =>
    apiClient.post<any[]>("/comparison/comparison/", { product_ids: ids }),

  saveToFavorites: (ids: number[]) =>
    apiClient.post("/comparison/favorites/", { product_ids: ids }),

  getFavorites: () => apiClient.get<FavoriteEntry[]>("/comparison/favorites/"),

  deleteFavorite: (id: number) => apiClient.delete(`/comparison/favorites/${id}/`),
};
