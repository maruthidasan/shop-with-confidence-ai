export default function ProductArt({
  palette = "from-stone-100 to-stone-300",
  garment = "bg-stone-700",
  name,
  image,
  large = false,
}: {
  palette?: string;
  garment?: string;
  name: string;
  image?: string;
  large?: boolean;
}) {
  return (
    <div className={`relative overflow-hidden bg-stone-100 ${large ? "h-[35rem] sm:h-[43rem]" : "h-72"}`}>
      {image ? (
        <img
          src={image}
          alt={`Original product image of ${name}`}
          className="h-full w-full object-cover object-top transition duration-700"
          loading={large ? "eager" : "lazy"}
        />
      ) : (
        <div className={`relative grid h-full w-full overflow-hidden bg-gradient-to-br ${palette}`}>
          <div className={`relative mx-auto self-end rounded-t-[4.5rem] ${garment} ${large ? "h-[78%] w-[45%]" : "h-48 w-28"} shadow-[0_22px_30px_rgba(20,20,20,.18)]`} />
          <span className="sr-only">Original illustration of {name}</span>
        </div>
      )}
    </div>
  );
}
