type Props = {
  data: any;
  bg: string;
};

export default function ShortCompareCard({ data, bg }: Props) {
  if (!data) return null;

  return (
    <div className={bg}>
      <div className="short-img-wrapper">
        {data.img && (
          <img
            className="short-img"
            src={data.img}
            alt={data.name}
            loading="lazy"
          />
        )}
      </div>

      <h3>{data.name}</h3>
      <h4>Характеристики</h4>

      {data.characteristics_groups.map((group: any) => (
        <div key={group.name} className="short-block">
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
