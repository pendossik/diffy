import Records from "../../records.json";

type Props = {
  productName: string;
  bg: string;
};

export default function CompareCard({ productName, bg }: Props) {
  const productData = Records.find((record) => record.name === productName);

  return (
    productData && (
      <div className={bg}>
        <img className="card" src={productData.img} alt={productData.name} />
        <h3>{productData.name}</h3>
        <h4>Характеристики</h4>
        <div className="short-char">
          <h4>Ширина</h4>
          <p>{productData.size?.width}</p>
        </div>
        <div className="short-char">
          <h4>Высота</h4>
          <p>{productData.size?.height}</p>
        </div>
        <div className="short-char">
          <h4>Толщина</h4>
          <p>{productData.size?.thickness}</p>
        </div>
        <div className="short-char">
          <h4>Вес</h4>
          <p>{productData.weight}</p>
        </div>
        <div className="short-char">
          <h4>Тип матрицы</h4>
          <p>{productData.display.type}</p>
        </div>
        <div className="short-char">
          <h4>Размер экрана</h4>
          <p>{productData.display.size}</p>
        </div>
        <div className="short-char">
          <h4>Разрешение экрана</h4>
          <p>{productData.display.resolution}</p>
        </div>
        <div className="short-char">
          <h4>Частота</h4>
          <p>{productData.display.frequency}</p>
        </div>
        <div className="short-char">
          <h4>Процессор</h4>
          <p>{productData.cpu?.model}</p>
        </div>
        <div className="short-char">
        <h4>Операционная система</h4>
          <p>{productData.os}</p>
        </div>
        <div className="short-char">
        <h4>Размер батареи</h4>
          <p>{productData.battery}</p>
        </div>
        <div className="short-char">
        <h4>Оперативная память</h4>
          <p>{productData.ram}</p>
        </div>
        <div className="short-char">
        <h4>Память</h4>
          <p>{productData.storage}</p>
        </div>
      </div>
    )
  );
}
