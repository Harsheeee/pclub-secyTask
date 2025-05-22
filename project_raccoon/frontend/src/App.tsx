import { Routes, Route } from 'react-router-dom';
import Home from './Components/Home';
import Dashboard from './Components/Dashboard';
import Login from './Components/Login';
import Register from './Components/Register';



const App: React.FC = () => {
  
    return (
    <Routes>
      
      <Route path="/" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/home" element={<Home />} />
      <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/login" element={<Login />} />
    </Routes>
  );
}

export default App;
