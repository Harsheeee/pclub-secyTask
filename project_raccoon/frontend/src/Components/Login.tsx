import { useState } from 'react'
import axios from 'axios'
import { useNavigate } from "react-router-dom";

function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const navigate = useNavigate();

  const handleLogin = async () => {
    try {
      const res = await axios.post('http://localhost:5000/login', { username, password })
      localStorage.setItem('token', res.data.access_token)
      alert('Login successful!')
      navigate('/home');
    } catch (err: any) {
      alert(err.response.data.message)
      if (err.response.data.message === "User not found") {
        navigate('/register');
      }
    }
  }

  return (
    <div className="login">
      <h1>Welcome to Project Raccoon</h1>
      <h2>Login</h2>
      <input placeholder="Username" onChange={e => setUsername(e.target.value)} />
      <input type="password" placeholder="Password" onChange={e => setPassword(e.target.value)} />
      <button onClick={handleLogin}>Login</button>
    </div>
  )
}

export default Login
