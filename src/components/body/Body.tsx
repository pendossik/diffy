import './body.css'
import Search from './Search';
import { useState} from 'react';
import CompareCard from './CompareCard';


export function Body() {
    const [firstProduct, setFirstProduct] = useState({ id: 0, name: "" });
    const [secondProduct, setSecondProduct] = useState({ id: 0, name: "" });
    const [showComparison, setShowComparison] = useState(false);

    
  

    return (
        <main className="comparison-form">
            <h1 className="visually-hidden">Сравнение объектов - секция</h1>
            <div className="comparison-form__container">
                <div className="comparison-form__inputs-column">
                    <div className="comparison-form__input-wrapper">
                        <Search
                            text="Напишите название первого товара для сравнения"
                            value={firstProduct.name}
                            onChange={(id, name) => setFirstProduct({ id, name })}
                        />
                    </div>

                    <img src="./src/icons/Plus.svg" alt="плюс" className="comparison-form__plus" />

                    <div className="comparison-form__input-wrapper">
                        <Search
                            text="Напишите название второго товара для сравнения"
                            value={secondProduct.name}
                            onChange={(id, name) => setSecondProduct({ id, name })}
                        />
                    </div>
                </div>

                <div className="comparison-form__button-column">
                    <button
                        onClick={() => setShowComparison(true)}
                        className="comparison-form__compare-button"
                    >
                        Сравнить
                    </button>
                </div>
            </div>

            {showComparison && (
                <div className="comparison-form__results">
                    <CompareCard productId={firstProduct.id} />
                    <CompareCard productId={secondProduct.id} />
                </div>
            )}
        </main>
    )
};