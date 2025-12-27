// import Records from "../../records.json";
// import "./compare.css";

// type Props = {
//   productName: string;
//   className: string;
// };

// export default function FullCompareCard({
//   productName,
//   className = "",
// }: Props) {
//   const productData = Records.find((record) => record.name === productName);

//   return (
//     productData && (
//       <div className="card">
//         <div className="char-header">
//           <h3 className={className}>Дисплей</h3>
//         </div>
//         <h4 className={className}>Размер</h4>
//         <div className="char">
//           <p>{productData.display.size}</p>
//         </div>
//         <h4 className={className}>Разрешение</h4>
//         <div className="char">
//           <p>{productData.display.resolution}</p>
//         </div>
//         <h4 className={className}>Тип матрицы</h4>
//         <div className="char">
//           <p>{productData.display.type}</p>
//         </div>
//         <h4 className={className}>Частота</h4>
//         <div className="char">
//           <p>{productData.display.frequency}</p>
//         </div>
//       </div>
//     )
//   );
// }
