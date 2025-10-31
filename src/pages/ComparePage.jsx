import '../index.css';
import Header from '../components/Header';
import Footer from '../components/Footer';
import CompareCard from '../components/CompareCard';
import { useLocation } from 'react-router-dom';




//ЭТО ОТДЕЛЬНАЯ СТРАНИЦА ДЛЯ СРАВНЕНИЯ, Я ЕЕ ОСТАВИЛ НА ВСЯКИЙ СЛУЧАЙ



export default function ComparePage(){
    const location = useLocation();
    const {firstProduct, secondProduct} = location.state;

    return(
    <div>
        <Header />
        <div className='compare'>
            <CompareCard 
                product={firstProduct} 
            />
            <CompareCard 
                product={secondProduct}
            />
        </div>
        <Footer />
    </div>
    );
}