import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Body } from './components/body/Body'
import Header from './components/header/Header'
import Footer from './components/footer/Footer'
import { Login } from './components/auth/login/Login';
import { Register } from './components/auth/register/Register';
import { Compare } from './components/body/Compare';


function App() {

  return (
    <BrowserRouter>
      <Header />
      <main>
        <Routes>
          <Route path='/' element={<Body />}/>  
          <Route path='/compare' element={<Compare />}/>
          <Route path='/login' element={<Login />}/>
          <Route path='/register' element={<Register />}/>
        </Routes>
      </main>
      <Footer />
    </BrowserRouter>
  )
}

export default App
