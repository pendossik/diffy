import { apiClient } from "../apiClient";
import { type Product } from "../../types/product";

export type FavoriteEntry = {
  id: number;
  products: Product[];
  created_at: string;
};

export const productService = {
  getAllProducts: () => apiClient.get<Product[]>("/compare/products/"),

  compare: (ids: number[]) =>
    apiClient.post<any[]>("/compare/comparison/", { product_ids: ids }),

  saveToFavorites: (ids: number[]) =>
    apiClient.post("/compare/favorites/", { product_ids: ids }),

  getFavorites: () => apiClient.get<FavoriteEntry[]>("/compare/favorites/"),

  deleteFavorite: (id: number) => apiClient.delete(`/compare/favorites/${id}/`),
};
