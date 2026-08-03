import { useState } from 'react';
import { addDishesToPlan } from '../api/weeklyPlans';
import { getDishLabel } from '../utils/dish';
import { DAYS, DAY_LABELS, MEALS, MEAL_LABELS } from '../constants/labels';

function WeeklyPlanCard({ plan, dishes, onDeletePlan, onDeleteEntry, onEntriesAdded }) {
  const [pendingEntries, setPendingEntries] = useState([]);
  const [day, setDay] = useState(DAYS[0]);
  const [meal, setMeal] = useState(MEALS[0]);
  const [dishId, setDishId] = useState('');
  const [error, setError] = useState('');

  function handleAddToPending(event) {
    event.preventDefault();
    const newEntry = { day_of_week: day, meal_type: meal, dish_public_id: dishId };
    setPendingEntries([...pendingEntries, newEntry]);
    setDishId('');
  }

  function handleRemovePending(index) {
    setPendingEntries(pendingEntries.filter((_, i) => i !== index));
  }

  async function handleSaveAll() {
    setError('');
    try {
      await addDishesToPlan(plan.id, pendingEntries);
      setPendingEntries([]);
      onEntriesAdded();
    } catch (err) {
      setError('Errore: uno o più piatti non validi. Nessuna voce salvata.');
    }
  }

  function dishLabelById(id) {
    const dish = dishes.find((d) => d.id === id);
    return dish ? getDishLabel(dish) : '?';
  }

  return (
    <div style={{ border: '1px solid #ccc', padding: '1rem', marginBottom: '1rem' }}>
      <h2>
        {plan.name} {plan.is_default && '(default)'}
        <button onClick={onDeletePlan}>Elimina piano</button>
      </h2>

      <h3>Voci salvate</h3>
      <ul>
        {plan.dishes.map((entry) => (
          <li key={entry.id}>
            {DAY_LABELS[entry.day_of_week]} — {MEAL_LABELS[entry.meal_type]} — {getDishLabel(entry.dish)}
            <button onClick={() => onDeleteEntry(entry.id)}>Rimuovi</button>
          </li>
        ))}
      </ul>

      <h3>Componi la settimana</h3>
      <form onSubmit={handleAddToPending}>
        <select value={day} onChange={(e) => setDay(e.target.value)}>
          {DAYS.map((d) => <option key={d} value={d}>{DAY_LABELS[d]}</option>)}
        </select>
        <select value={meal} onChange={(e) => setMeal(e.target.value)}>
          {MEALS.map((m) => <option key={m} value={m}>{MEAL_LABELS[m]}</option>)}
        </select>
        <select value={dishId} onChange={(e) => setDishId(e.target.value)} required>
          <option value="">Scegli piatto</option>
          {dishes.map((d) => (
            <option key={d.id} value={d.id}>
              {getDishLabel(d)}
            </option>
          ))}
        </select>
        <button type="submit">Aggiungi alla lista</button>
      </form>

      {pendingEntries.length > 0 && (
        <div>
          <h4>Voci da salvare:</h4>
          <ul>
            {pendingEntries.map((entry, index) => (
              <li key={index}>
                {DAY_LABELS[entry.day_of_week]} — {MEAL_LABELS[entry.meal_type]} — {dishLabelById(entry.dish_public_id)}
                <button onClick={() => handleRemovePending(index)}>Rimuovi</button>
              </li>
            ))}
          </ul>
          <button onClick={handleSaveAll}>Salva tutte le voci</button>
        </div>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}
    </div>
  );
}

export default WeeklyPlanCard;