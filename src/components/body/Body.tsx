import './body.css'

export function Body() {
    return(
        <main className="comparison-form">
            <h1 className="visually-hidden">Сравнение объктов - секция</h1>
            <div className="comparison-form__inner">
                <div className="comparison-form__inputs-column">
                    <div className="comparison-form__input-wrapper">
                        <label className="visually-hidden" htmlFor="product1"></label>
                        <input id='product1' className="" type="text" placeholder="Название первого товара"/>
                    </div>

                    <img src="./src/icons/Plus.svg" alt="image plus"  className="main__image-plus"/>

                    <div className="comparison-form__input-wrapper">
                        <label className="visually-hidden" htmlFor="product2"></label>
                        <input id='product2' className="" type="text" placeholder="Название второго товара"/>
                    </div>
                </div>
                
                <button className="comparison-form__compare-button">Сравнить</button>
            </div>
        </main>
    )
}