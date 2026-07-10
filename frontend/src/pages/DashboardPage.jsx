import { useAuth } from '../context/AuthContext';

function DashboardPage() {
  const { logout } = useAuth();

  return (
    <div>
      <h1>Dashboard</h1>
      <p>Login riuscito!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}

export default DashboardPage;