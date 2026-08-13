import StoreHeader from "@/components/store/StoreHeader";
import ProductFilters from "@/components/store/ProductFilters";
import { products, type Product } from "@/components/store/catalog";

export default async function ShopPage({ searchParams }: { searchParams: Promise<{ category?: string }> }) {
  const { category } = await searchParams;
  const categories = new Set<Product["category"]>(["New Arrivals", "Men", "Women", "Accessories"]);
  const initialCategory = category && categories.has(category as Product["category"]) ? category : "All";
  return <main className="min-h-screen bg-[#fbfaf8]"><StoreHeader /><section className="mx-auto max-w-7xl px-5 py-14 sm:px-8"><p className="text-xs font-semibold tracking-[.2em] text-stone-500">THE COLLECTION</p><h1 className="mt-3 text-5xl font-medium tracking-[-.05em]">Pieces that make<br />sense for your life.</h1><p className="mt-5 max-w-xl leading-7 text-stone-600">A considered wardrobe of modern essentials, occasion pieces and thoughtful finishing touches.</p><ProductFilters products={products} initialCategory={initialCategory} /></section></main>;
}
