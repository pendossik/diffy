import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import HomePage from './HomePage';
import ComparePage from './ComparePage';
import './index.css';

export default function App() { 
  return (
    <div>
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/compare" element={<ComparePage />} />
        </Routes>
      </Router>
    </div>

  );
}