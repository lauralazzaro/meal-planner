import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';

function DashboardPage() {
  const { logout } = useAuth();

  const navigationLinks = [
    { to: '/ingredients', label: 'Ingredienti' },
    { to: '/dishes', label: 'Piatti' },
    { to: '/shopping-lists', label: 'Liste della spesa' },
  ];

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Bentornata!</p>

      <nav>
        <ul>
          {navigationLinks.map((link) => (
            <li key={link.to}>
              <Link to={link.to}>{link.label}</Link>
            </li>
          ))}
        </ul>
      </nav>

      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default DashboardPage;