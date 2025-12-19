type Props = {
  data: any;
  bg: string;
};

export default function ShortCompareCard({ data, bg }: Props) {
  if (!data) return null;

  return (
    <div className={bg}>
      <img className="card" src={data.img} alt={data.name} />

      <h3>{data.name}</h3>
      <h4>Характеристики</h4>

      {data.characteristics_groups.map((group: any) => (
        <div key={group.name} className="short-group">
          {group.characteristics.map((c: any) => (
            <div key={c.id} className="short-char">
              <h4>{c.name}</h4>
              <p>{c.value}</p>
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}
