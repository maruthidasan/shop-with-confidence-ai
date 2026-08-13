import Link from "next/link";
import { Product } from "./catalog";
import ProductArt from "./ProductArt";

const categoryPhotos: Record<Product["category"], string> = {
  "New Arrivals": "/products/08_Cashmere_Wrap_Coat_Women.jpg",
  Men: "/products/01_Navy_Sculpted_Blazer_Men.jpg",
  Women: "/products/04_Silk_Column_Dress_Women.jpg",
  Accessories: "/images/accessories-editorial.png",
};

const productPhotos: Record<string, string> = {
  "relaxed-trouser": "/products/08_Cashmere_Wrap_Coat_Women.jpg",
  "everyday-coat": "/products/08_Cashmere_Wrap_Coat_Women.jpg",
  "sculpted-knit": "/products/02_Soft_Shoulder_Jacket_Women.jpg",
  "draped-shirt": "/products/04_Silk_Column_Dress_Women.jpg",
  "soft-tailored-blazer": "/products/01_Navy_Sculpted_Blazer_Men.jpg",
  "men-overshirt": "/products/07_Relaxed_Linen_Shirt_Men.jpg",
  "men-polo": "/products/05_Fine_Gauge_Polo_Men.jpg",
  "men-field-jacket": "/products/03_Modern_Field_Jacket_Men.jpg",
  "men-topcoat": "/products/01_Navy_Sculpted_Blazer_Men.jpg",
  "men-merino-crew": "/products/05_Fine_Gauge_Polo_Men.jpg",
  "women-soft-jacket": "/products/02_Soft_Shoulder_Jacket_Women.jpg",
  "women-cardigan": "/products/08_Cashmere_Wrap_Coat_Women.jpg",
  "women-pleated-midi": "/products/06_Rib_Knit_Dress_Women.jpg",
  "women-satin-cami": "/products/04_Silk_Column_Dress_Women.jpg",
  "women-wide-leg": "/products/02_Soft_Shoulder_Jacket_Women.jpg",
  "acc-loafer": "/images/accessories-loafer.png",
  "acc-crossbody": "/images/accessories-crossbody.png",
  "acc-scarf": "/images/accessories-scarf.png",
  "acc-sunglasses": "/images/accessories-sunglasses.png",
  "acc-watch": "/images/accessories-watch.png",
};

export default function ProductCard({ product }: { product: Product }) {
  return (
    <article className="group">
      <Link href={`/product/${product.id}`} className="block overflow-hidden">
        <ProductArt
          palette={product.palette}
          garment={product.garment}
          name={product.name}
          image={productPhotos[product.id] ?? categoryPhotos[product.category]}
        />
        <div className="mt-4 flex items-start justify-between gap-3">
          <div>
            <p className="text-sm font-medium text-stone-900">{product.name}</p>
            <p className="mt-1 text-sm text-stone-500">{product.color} · {product.material}</p>
          </div>
          <p className="shrink-0 text-sm font-medium">${product.price}</p>
        </div>
      </Link>
      <div className="mt-3 flex items-center justify-between">
        <span className="text-xs text-stone-500">★ {product.rating}</span>
        <Link href="/upload" className="text-xs font-medium text-violet-700 opacity-0 transition group-hover:opacity-100 focus:opacity-100">
          AI Stylist →
        </Link>
      </div>
    </article>
  );
}
