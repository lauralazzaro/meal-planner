import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import IngredientsPage from './pages/IngredientsPage';
import DishesPage from './pages/DishesPage';
import WeeklyPlansPage from './pages/WeeklyPlansPage';
import ShoppingListsPage from './pages/ShoppingListsPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  const { isAuthenticated } = useAuth();

  return (
    <div className={isAuthenticated ? 'app-shell' : ''}>
      <Sidebar />
      <main className={isAuthenticated ? 'app-content container' : 'container'}>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
          <Route path="/ingredients" element={<ProtectedRoute><IngredientsPage /></ProtectedRoute>} />
          <Route path="/dishes" element={<ProtectedRoute><DishesPage /></ProtectedRoute>} />
          <Route path="/weekly-plans" element={<ProtectedRoute><WeeklyPlansPage /></ProtectedRoute>} />
          <Route path="/shopping-lists" element={<ProtectedRoute><ShoppingListsPage /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;