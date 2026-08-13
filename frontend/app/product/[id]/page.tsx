import { notFound } from "next/navigation";
import StoreHeader from "@/components/store/StoreHeader";
import ProductDetail from "@/components/store/ProductDetail";
import { products } from "@/components/store/catalog";
export default async function ProductPage({ params }: { params: Promise<{ id: string }> }) { const { id } = await params; const product = products.find(item=>item.id===id); if (!product) notFound(); const related = products.filter(item=>item.id!==id && (item.category===product.category || item.occasion===product.occasion)); return <main className="min-h-screen bg-[#fbfaf8]"><StoreHeader/><section className="mx-auto max-w-7xl px-5 py-7 sm:px-8"><p className="mb-7 text-sm text-stone-500">Shop / {product.category} / <span className="text-stone-900">{product.name}</span></p><ProductDetail product={product} related={related}/></section></main>; }
