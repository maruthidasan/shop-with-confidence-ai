import Link from "next/link";

const collectionImages = [
  "/products/08_Cashmere_Wrap_Coat_Women.jpg",
  "/products/01_Navy_Sculpted_Blazer_Men.jpg",
  "/products/04_Silk_Column_Dress_Women.jpg",
  "/images/accessories-editorial.png",
  "/products/08_Cashmere_Wrap_Coat_Women.jpg",
];

const palettes = [
  "from-[#e6ded2] to-[#c7b49d]",
  "from-[#d7dfd2] to-[#8d9a82]",
  "from-[#d9e7ec] to-[#97bdc9]",
  "from-[#d9c5c6] to-[#8b6264]",
  "from-[#e9e7e0] to-[#aaa79e]",
  "from-[#d7d3df] to-[#807a91]",
];

export default function CollectionCard({ title, index }: { title: string; index: number }) {
  const image = collectionImages[index];

  return (
    <Link href={`/shop?category=${encodeURIComponent(title)}`} className="group relative block h-96 overflow-hidden rounded-sm">
      {image ? (
        <img
          src={image}
          alt={title}
          className="absolute inset-0 h-full w-full object-cover transition duration-700 group-hover:scale-[1.03]"
          loading="lazy"
        />
      ) : (
        <div className={`absolute inset-0 bg-gradient-to-br ${palettes[index]}`} />
      )}
      <div className="absolute inset-0 bg-gradient-to-t from-black/65 via-black/5 to-transparent" />
      <div className="absolute inset-x-0 bottom-0 p-6 text-white">
        <p className="text-xl font-medium tracking-tight">{title}</p>
        <p className="mt-2 text-sm text-white/80">Explore the edit →</p>
      </div>
    </Link>
  );
}
