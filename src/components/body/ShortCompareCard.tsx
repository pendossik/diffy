type Props = {
  data: any;
  bg: string;
};

export default function ShortCompareCard({ data, bg }: Props) {
  if (!data) return null;

  const getValue = (name: string) =>
    data.characteristics.find((c: any) => c.name === name)?.value || "—";

  return (
    <div className={bg}>
      <img className="card" src={getValue("Фото")} alt={data.name} />

      <h3>{data.name}</h3>
      <h4>Характеристики</h4>

      {data.characteristics.map((c: any) => (
        <div className="short-char">
          <h4>{c.name}</h4>
          <p>{c.value}</p>
        </div>
      ))}
    </div>
  );
}
