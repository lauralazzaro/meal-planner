import { useState, useEffect } from 'react';
import { getWeeklyPlans, createWeeklyPlan, deleteWeeklyPlan, deleteDishFromPlan } from '../api/weeklyPlans';
import { getDishes } from '../api/dishes';
import WeeklyPlanCard from '../components/WeeklyPlanCard';

function WeeklyPlansPage() {
  const [plans, setPlans] = useState([]);
  const [dishes, setDishes] = useState([]);
  const [newPlanName, setNewPlanName] = useState('');
  const [isDefault, setIsDefault] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadPlans();
    loadDishes();
  }, []);

  async function loadPlans() {
    try {
      const data = await getWeeklyPlans();
      setPlans(data);
    } catch (err) {
      setError('Errore nel caricamento dei piani.');
    }
  }

  async function loadDishes() {
    const data = await getDishes();
    setDishes(data);
  }

  async function handleCreatePlan(event) {
    event.preventDefault();
    await createWeeklyPlan(newPlanName, isDefault);
    setNewPlanName('');
    setIsDefault(false);
    loadPlans();
  }

  async function handleDeletePlan(id) {
    await deleteWeeklyPlan(id);
    loadPlans();
  }

  async function handleDeleteEntry(planId, entryId) {
    await deleteDishFromPlan(planId, entryId);
    loadPlans();
  }

  return (
    <div>
      <h1>Piani settimanali</h1>

      <form onSubmit={handleCreatePlan}>
        <input
          type="text"
          placeholder="Nome piano"
          value={newPlanName}
          onChange={(e) => setNewPlanName(e.target.value)}
          required
        />
        <label>
          <input
            type="checkbox"
            checked={isDefault}
            onChange={(e) => setIsDefault(e.target.checked)}
          />
          Imposta come default
        </label>
        <button type="submit">Crea piano</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {plans.map((plan) => (
        <WeeklyPlanCard
          key={plan.id}
          plan={plan}
          dishes={dishes}
          onDeletePlan={() => handleDeletePlan(plan.id)}
          onDeleteEntry={(entryId) => handleDeleteEntry(plan.id, entryId)}
          onEntriesAdded={loadPlans}
        />
      ))}
    </div>
  );
}

export default WeeklyPlansPage;