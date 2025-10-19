import './body.css'

export function Body() {
    return(
        <main className="comparison-form">
            <h1 className="visually-hidden">Сравнение объктов - секция</h1>
            <div className="comparison-form__inner">
                <div className="comparison-form__two-input">
                    <label className="visually-hidden" htmlFor="product1"></label>
                    <input id='product1' className="" type="text" placeholder="Введите название первого товара для сравнения"/>
                    <img src="./src/icons/Plus.svg" alt="image plus"  className="main__image-plus"/>
                    <label className="visually-hidden" htmlFor="product2"></label>
                    <input id='product2' className="" type="text" placeholder="Введите название второго товара для сравнения"/>
                </div>
                <div className="comparison-form__result-compare">
                    <button className="comparison-form__compare-button">Сравнить</button>
                </div>
            </div>
        </main>
    )
}