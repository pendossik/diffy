import './body.css'
import Button from './Button';
import Search from './Search';
import { useState, FormEvent  } from 'react';
import CompareCard from './CompareCard';


export function Body() {
    const [firstProduct, setFirstProduct] = useState('');
    const [secondProduct, setSecondProduct] = useState('');
    const [showComparison, setShowComparison] = useState(false);

    const handleCompare = (e: FormEvent) => {
        e.preventDefault();
        setShowComparison(true);
    }

    return(
        <main className="comparison-form">
            <h1 className="visually-hidden">Сравнение объктов - секция</h1>
            <div className="comparison-form__inner">
                <div className="comparison-form__inputs-column">
                    <div className="comparison-form__input-wrapper">
                        <Search 
                            text="Название первого товара"
                            value={firstProduct}
                            onChange={(e) => setFirstProduct(e.target.value)}
                        />
                    </div>

                    <img src="./src/icons/Plus.svg" alt="image plus"  className="main__image-plus"/>

                    <div className="comparison-form__input-wrapper">
                        <Search 
                            text="Название второго товара"
                            value={secondProduct}
                            onChange={(e) => setSecondProduct(e.target.value)}
                        />
                    </div>
                </div>
                
                 <Button text={'Сравнить'} onClick={handleCompare}/>
            </div>

            {showComparison && (
                <div className="comparison-form__results">
                    <CompareCard product={firstProduct} />
                    <CompareCard product={secondProduct} />
                </div>
            )}
        </main>
    )
}