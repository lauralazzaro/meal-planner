import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { registerUser } from '../api/auth';

function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');

    try {
      await registerUser(email, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 1500);
    } catch (err) {
      if (err.response?.status === 409) {
        setError('Questa email è già registrata.');
      } else {
        setError('Errore durante la registrazione.');
      }
    }
  };

  return (
    <div>
      <h1>Registrati</h1>
      {success ? (
        <p>Registrazione avvenuta con successo! Reindirizzamento al login...</p>
      ) : (
        <form onSubmit={handleSubmit}>
          <div>
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              minLength={8}
              required
            />
          </div>
          {error && <p style={{ color: 'red' }}>{error}</p>}
          <button type="submit">Registrati</button>
        </form>
      )}
      <p>
        Hai già un account? <Link to="/login">Accedi</Link>
      </p>
    </div>
  );
}

export default RegisterPage;