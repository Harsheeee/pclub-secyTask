import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from "react-router-dom";

function Register() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate();

  const handleRegister = async () => {
    try {
      const res = await axios.post('http://localhost:5000/register', { username, password })
      localStorage.setItem('token', res.data.access_token)
      //alert(res.data.message)
      navigate('/home');
    } catch (err: any) {
      alert(err.response.data.message)
    }
  }
  const oldUser = () => {
    navigate('/login');
  }

  return (
    <div className="login">
      <h1>Welcome to Project Raccoon</h1>
      <h2>Register</h2>
      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} onKeyDown={e=>{
        if (e.key === 'Enter') {
          handleRegister();
        }
      }} />
      <button onClick={handleRegister}>Register</button>
      <p>Already have an account? <a href="#" onClick={oldUser}>Login here</a></p>
    </div>
  )
}

export default Register
