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
      alert(res.data.message)
      navigate('/home');
    } catch (err: any) {
      alert(err.response.data.message)
    }
  }

  return (
    <div className="login">
      <h1>Welcome to Project Raccoon</h1>
      <h2>Register</h2>
      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={handleRegister}>Register</button>
    </div>
  )
}

export default Register
