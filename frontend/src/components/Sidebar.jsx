import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { decodeJwtPayload } from '../utils/jwt';

function Sidebar() {
  const { token, logout, isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) return null;

  const links = [
    { to: '/', label: 'Dashboard', icon: 'dashboard' },
    { to: '/ingredients', label: 'Ingredienti', icon: 'inventory_2' },
    { to: '/dishes', label: 'Piatti', icon: 'restaurant_menu' },
    { to: '/weekly-plans', label: 'Piano settimanale', icon: 'calendar_month' },
    { to: '/shopping-lists', label: 'Liste della spesa', icon: 'shopping_cart' },
  ];

  const email = decodeJwtPayload(token)?.sub;

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <h1>Meal Planner</h1>
        <p>Healthy Living</p>
      </div>
      <ul className="sidebar-links">
        {links.map((link) => (
          <li key={link.to}>
            <Link
              to={link.to}
              className={location.pathname === link.to ? 'active' : ''}
            >
              <span className="material-symbols-outlined">{link.icon}</span>
              <span>{link.label}</span>
            </Link>
          </li>
        ))}
      </ul>
      <div className="sidebar-footer">
        {email && <p className="sidebar-user-email">{email}</p>}
        <button onClick={logout}>Logout</button>
      </div>
    </aside>
  );
}

export default Sidebar;
