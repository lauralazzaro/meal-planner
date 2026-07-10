import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

function DashboardPage() {
  const { logout } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Login riuscito!</p>
      <p>
        <Link to="/ingredients">Ingredients</Link>
      </p>
      <p>
        <Link to="/dishes">Dishes</Link>
      </p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default DashboardPage;