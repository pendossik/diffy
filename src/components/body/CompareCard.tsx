import Records from '../../records.json';

type Props = {
  productName: string;
};

export default function CompareCard({productName}: Props){

    const productData = Records.find(record => record.name === productName);

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