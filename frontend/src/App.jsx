import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import IngredientsPage from './pages/IngredientsPage';
import DishesPage from './pages/DishesPage';
import ShoppingListsPage from './pages/ShoppingLists';
import WeeklyPlansPage from './pages/WeeklyPlansPage';

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/ingredients"
        element={
          <ProtectedRoute>
            <IngredientsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/dishes"
        element={
          <ProtectedRoute>
            <DishesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/shopping-lists"
        element={
          <ProtectedRoute>
            <ShoppingListsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/weekly-plans"
        element={
          <ProtectedRoute>
            <WeeklyPlansPage />
          </ProtectedRoute>
        }
      />
    </Routes>
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