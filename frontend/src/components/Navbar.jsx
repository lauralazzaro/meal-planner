import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function Navbar() {
  const { logout, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return null;

  const links = [
    { to: '/', label: 'Dashboard' },
    { to: '/ingredients', label: 'Ingredienti' },
    { to: '/dishes', label: 'Piatti' },
    { to: '/weekly-plans', label: 'Piano settimanale' },
    { to: '/shopping-lists', label: 'Liste della spesa' },
  ];

  return (
    <nav className="navbar">
      <div className="navbar-brand">Meal Planner</div>
      <ul className="navbar-links">
        {links.map((link) => (
          <li key={link.to}>
            <Link
              to={link.to}
              className={location.pathname === link.to ? 'active' : ''}
            >
              {link.label}
            </Link>
          </li>
        ))}
      </ul>
      <button onClick={logout}>Logout</button>
    </nav>
  );
}

export default Navbar;