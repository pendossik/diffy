import './index.css';
import Records from './records.json';

export default function CompareCard({product}){


    const productData = Records.find(record => record.name === product);

    return(
      productData && (
        <div className='card'>
          <h2>{productData.name}</h2>
          <hr/>
          <img className='card' src={productData.img} alt={productData.name}/>
          <hr/>
          <h3>Характеристики</h3>
          <p></p>
        </div>
      )
    );
}